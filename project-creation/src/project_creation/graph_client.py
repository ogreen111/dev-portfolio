"""Audited, retrying Microsoft Graph transport."""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.parse import urlparse

import httpx
from rfp_automation.graph_cloud import graph_base

RETRYABLE_STATUSES = frozenset({429, 502, 503, 504})
AUTOMATIC_RETRY_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


class TokenProvider(Protocol):
    def get_token(self) -> str: ...


@dataclass(frozen=True, slots=True)
class GraphResponse:
    status: int
    headers: Mapping[str, str]
    json_body: object | None
    byte_chunks: Iterable[bytes]

    def json(self) -> object:
        return self.json_body

    def iter_bytes(self) -> Iterator[bytes]:
        yield from self.byte_chunks


class GraphTransport(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        params: Mapping[str, str] | None = None,
        json: object | None = None,
        stream: bool = False,
    ) -> GraphResponse: ...


def _stream_and_close(response: httpx.Response) -> Iterator[bytes]:
    try:
        yield from response.iter_bytes()
    finally:
        response.close()


class HttpxGraphTransport:
    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client or httpx.Client(timeout=30, follow_redirects=True)

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        params: Mapping[str, str] | None = None,
        json: object | None = None,
        stream: bool = False,
    ) -> GraphResponse:
        request_obj = self._client.build_request(
            method, url, headers=headers, params=params, json=json
        )
        response = self._client.send(request_obj, stream=True)
        # Only success responses are handed back as an open, lazily-drained
        # stream. Error/retryable responses are read and closed here so the
        # caller (which never iterates a discarded GraphResponse) can't leak
        # the connection.
        if stream and 200 <= response.status_code < 300:
            return GraphResponse(
                status=response.status_code,
                headers=dict(response.headers),
                json_body=None,
                byte_chunks=_stream_and_close(response),
            )
        try:
            response.read()
        finally:
            response.close()
        json_body: object | None = None
        if response.content:
            try:
                json_body = response.json()
            except ValueError:
                json_body = None
        return GraphResponse(
            status=response.status_code,
            headers=dict(response.headers),
            json_body=json_body,
            byte_chunks=(),
        )


@dataclass(frozen=True, slots=True)
class GraphCallAudit:
    method: str
    endpoint_class: str
    status: int
    duration_ms: int
    request_id: str | None


class GraphError(RuntimeError):
    def __init__(
        self,
        *,
        status: int,
        code: str,
        message: str,
        request_id: str | None,
        retryable: bool,
    ) -> None:
        super().__init__(f"Graph request failed ({status}, {code}): {message}")
        self.status = status
        self.code = code
        self.request_id = request_id
        self.retryable = retryable


def _header(headers: Mapping[str, str], name: str) -> str | None:
    lowered = name.lower()
    return next(
        (value for key, value in headers.items() if key.lower() == lowered),
        None,
    )


class GraphClient:
    def __init__(
        self,
        tokens: TokenProvider,
        transport: GraphTransport,
        *,
        base_url: str | None = None,
        audit: Callable[[GraphCallAudit], None] | None = None,
        sleeper: Callable[[float], None] = time.sleep,
        max_attempts: int = 4,
        max_backoff: float = 30,
    ) -> None:
        self._tokens = tokens
        self._transport = transport
        self._base_url = (base_url or graph_base()).rstrip("/")
        self._audit = audit or (lambda _: None)
        self._sleeper = sleeper
        self._max_attempts = max_attempts
        self._max_backoff = max_backoff

    def _url(self, path: str) -> str:
        if not path.startswith(("http://", "https://")):
            return f"{self._base_url}/{path.lstrip('/')}"
        expected = urlparse(self._base_url)
        actual = urlparse(path)
        if (actual.scheme, actual.netloc) != (expected.scheme, expected.netloc):
            raise GraphError(
                status=0,
                code="invalidNextLink",
                message="pagination URL has an unexpected origin",
                request_id=None,
                retryable=False,
            )
        return path

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        json: object | None = None,
        stream: bool = False,
    ) -> GraphResponse:
        url = self._url(path)
        correlation_id = str(uuid.uuid4())
        response: GraphResponse | None = None
        for attempt in range(self._max_attempts):
            started = time.monotonic()
            try:
                response = self._transport.request(
                    method,
                    url,
                    headers={
                        "Authorization": f"Bearer {self._tokens.get_token()}",
                        "client-request-id": correlation_id,
                        "return-client-request-id": "true",
                    },
                    params=params,
                    json=json,
                    stream=stream,
                )
            except httpx.TransportError as exc:
                self._audit(
                    GraphCallAudit(
                        method=method.upper(),
                        endpoint_class=self._endpoint_class(url),
                        status=0,
                        duration_ms=int((time.monotonic() - started) * 1000),
                        request_id=None,
                    )
                )
                retry_allowed = method.upper() in AUTOMATIC_RETRY_METHODS
                if not retry_allowed or attempt + 1 == self._max_attempts:
                    raise GraphError(
                        status=0,
                        code="transportError",
                        message=str(exc),
                        request_id=None,
                        retryable=retry_allowed,
                    ) from exc
                self._sleeper(min(2**attempt, self._max_backoff))
                continue
            self._audit(
                GraphCallAudit(
                    method=method.upper(),
                    endpoint_class=self._endpoint_class(url),
                    status=response.status,
                    duration_ms=int((time.monotonic() - started) * 1000),
                    request_id=_header(response.headers, "request-id"),
                )
            )
            if 200 <= response.status < 300:
                return response
            retry_allowed = method.upper() in AUTOMATIC_RETRY_METHODS
            if (
                response.status not in RETRYABLE_STATUSES
                or not retry_allowed
                or attempt + 1 == self._max_attempts
            ):
                raise self._error(response, method)
            retry_after = _header(response.headers, "Retry-After")
            try:
                delay = float(retry_after) if retry_after is not None else 2**attempt
            except ValueError:
                delay = 2**attempt
            self._sleeper(min(max(delay, 0), self._max_backoff))
        assert response is not None
        raise self._error(response, method)

    def iter_collection(
        self,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
    ) -> Iterator[dict[str, Any]]:
        next_path: str | None = path
        next_params = params
        while next_path is not None:
            body = self.request("GET", next_path, params=next_params).json()
            if not isinstance(body, dict):
                raise GraphError(
                    status=0,
                    code="invalidResponse",
                    message="collection response is not an object",
                    request_id=None,
                    retryable=False,
                )
            values = body.get("value", [])
            if not isinstance(values, list):
                raise GraphError(
                    status=0,
                    code="invalidResponse",
                    message="collection value is not a list",
                    request_id=None,
                    retryable=False,
                )
            for value in values:
                if isinstance(value, dict):
                    yield value
            raw_next = body.get("@odata.nextLink")
            next_path = str(raw_next) if raw_next else None
            next_params = None

    def _endpoint_class(self, url: str) -> str:
        path = urlparse(url).path
        relative = path.removeprefix(urlparse(self._base_url).path).strip("/")
        return relative.split("/", 1)[0] or "root"

    @staticmethod
    def _error(response: GraphResponse, method: str) -> GraphError:
        body = response.json()
        error = body.get("error", {}) if isinstance(body, dict) else {}
        code = str(error.get("code", "unknownError"))
        message = str(error.get("message", "Microsoft Graph request failed"))
        return GraphError(
            status=response.status,
            code=code,
            message=message,
            request_id=_header(response.headers, "request-id"),
            retryable=(
                response.status in RETRYABLE_STATUSES
                and method.upper() in AUTOMATIC_RETRY_METHODS
            ),
        )
