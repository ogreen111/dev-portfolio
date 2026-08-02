from collections.abc import Mapping
from typing import Any

import httpx
import pytest

from project_creation.graph_client import (
    GraphCallAudit,
    GraphClient,
    GraphError,
    GraphResponse,
    HttpxGraphTransport,
)


class Tokens:
    def get_token(self) -> str:
        return "top-secret-token"


class ScriptedTransport:
    def __init__(self, responses: list[GraphResponse]) -> None:
        self.responses = responses
        self.calls: list[dict[str, Any]] = []

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
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": dict(headers),
                "params": params,
                "json": json,
                "stream": stream,
            }
        )
        return self.responses.pop(0)


def response(
    status: int,
    body: object | None = None,
    headers: Mapping[str, str] | None = None,
) -> GraphResponse:
    return GraphResponse(
        status=status,
        headers=dict(headers or {}),
        json_body=body,
        byte_chunks=(),
    )


def test_graph_client_adds_correlation_id_and_audits_without_secrets_or_body() -> None:
    transport = ScriptedTransport([response(200, {"id": "site-1"})])
    audits: list[GraphCallAudit] = []
    client = GraphClient(Tokens(), transport, audit=audits.append)

    result = client.request("POST", "/sites/example", json={"secret": "body"})

    assert result.json() == {"id": "site-1"}
    call = transport.calls[0]
    assert call["headers"]["Authorization"] == "Bearer top-secret-token"
    assert call["headers"]["client-request-id"]
    assert call["headers"]["return-client-request-id"] == "true"
    serialized_audit = repr(audits[0])
    assert "top-secret-token" not in serialized_audit
    assert "body" not in serialized_audit
    assert audits[0].endpoint_class == "sites"
    assert audits[0].status == 200


def test_graph_client_retries_retryable_status_with_bounded_retry_after() -> None:
    transport = ScriptedTransport(
        [
            response(429, {"error": {"code": "throttled"}}, {"Retry-After": "99"}),
            response(200, {"value": []}),
        ]
    )
    sleeps: list[float] = []
    client = GraphClient(Tokens(), transport, sleeper=sleeps.append, max_backoff=8)

    assert client.request("GET", "/sites").status == 200
    assert sleeps == [8]
    assert len(transport.calls) == 2


def test_graph_client_does_not_retry_ambiguous_post_failure() -> None:
    transport = ScriptedTransport(
        [
            response(503, {"error": {"code": "unavailable"}}),
            response(201, {"id": "duplicate"}),
        ]
    )
    client = GraphClient(Tokens(), transport)

    with pytest.raises(GraphError) as caught:
        client.request("POST", "/groups", json={"displayName": "Project"})

    assert caught.value.status == 503
    assert not caught.value.retryable
    assert len(transport.calls) == 1


def test_graph_client_retries_transport_failure_only_for_safe_method() -> None:
    class FlakyTransport(ScriptedTransport):
        def request(self, *args: Any, **kwargs: Any) -> GraphResponse:
            if not self.calls:
                self.calls.append({"failed": True})
                raise httpx.ReadTimeout("temporary timeout")
            return super().request(*args, **kwargs)

    transport = FlakyTransport([response(200, {"id": "site"})])
    sleeps: list[float] = []
    client = GraphClient(Tokens(), transport, sleeper=sleeps.append)

    assert client.request("GET", "/sites/site").status == 200
    assert sleeps == [1]


def test_httpx_transport_reads_json_inside_stream_context() -> None:
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"id": "site"}, request=request)
        ),
        follow_redirects=True,
    )

    result = HttpxGraphTransport(client).request(
        "GET", "https://graph.microsoft.com/v1.0/sites/site", headers={}
    )

    assert result.json() == {"id": "site"}


def test_httpx_transport_follows_sharepoint_content_redirect() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "graph.microsoft.com":
            return httpx.Response(
                302,
                headers={"Location": "https://download.example/spec.pdf"},
                request=request,
            )
        return httpx.Response(200, content=b"specification", request=request)

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        follow_redirects=True,
    )
    result = HttpxGraphTransport(client).request(
        "GET",
        "https://graph.microsoft.com/v1.0/drives/d/items/i/content",
        headers={"Authorization": "Bearer token"},
        stream=True,
    )

    assert b"".join(result.iter_bytes()) == b"specification"


def test_graph_client_normalizes_non_retryable_json_error() -> None:
    transport = ScriptedTransport(
        [
            response(
                403,
                {"error": {"code": "accessDenied", "message": "No site grant"}},
                {"request-id": "request-1"},
            )
        ]
    )
    client = GraphClient(Tokens(), transport)

    with pytest.raises(GraphError) as caught:
        client.request("GET", "/sites/example")

    assert caught.value.status == 403
    assert caught.value.code == "accessDenied"
    assert caught.value.request_id == "request-1"
    assert not caught.value.retryable


def test_graph_client_paginates_only_same_graph_origin() -> None:
    transport = ScriptedTransport(
        [
            response(
                200,
                {
                    "value": [{"id": "1"}],
                    "@odata.nextLink": "https://graph.microsoft.com/v1.0/sites?page=2",
                },
            ),
            response(200, {"value": [{"id": "2"}]}),
        ]
    )
    client = GraphClient(Tokens(), transport)

    assert list(client.iter_collection("/sites")) == [{"id": "1"}, {"id": "2"}]

    hostile = ScriptedTransport(
        [
            response(
                200,
                {
                    "value": [],
                    "@odata.nextLink": "https://attacker.example/steal-token",
                },
            )
        ]
    )
    with pytest.raises(GraphError, match="origin"):
        list(GraphClient(Tokens(), hostile).iter_collection("/sites"))
