"""SharePoint site, drive, path, and file access through the Graph wrapper."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Protocol
from urllib.parse import quote, unquote, urlparse

from pydantic import Field

from project_creation.graph_client import GraphResponse
from project_creation.models import FrozenModel, SiteTarget


class GraphReader(Protocol):
    def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> GraphResponse: ...

    def iter_collection(
        self,
        path: str,
        **kwargs: Any,
    ) -> Iterator[dict[str, Any]]: ...


class DriveItem(FrozenModel):
    id: str
    name: str
    is_folder: bool
    size: int | None = None
    web_url: str | None = None
    child_count: int | None = Field(default=None, ge=0)

    @classmethod
    def from_graph(cls, record: dict[str, Any]) -> DriveItem:
        folder = record.get("folder")
        return cls(
            id=str(record["id"]),
            name=str(record.get("name", "")),
            is_folder=isinstance(folder, dict),
            size=int(record["size"]) if record.get("size") is not None else None,
            web_url=str(record["webUrl"]) if record.get("webUrl") else None,
            child_count=(
                int(folder["childCount"])
                if isinstance(folder, dict) and folder.get("childCount") is not None
                else None
            ),
        )


class SharePointClient:
    def __init__(self, graph: GraphReader, *, allowed_hosts: set[str]) -> None:
        if not allowed_hosts:
            raise ValueError("at least one SharePoint hostname is required")
        self._graph = graph
        self._allowed_hosts = {host.rstrip(".").lower() for host in allowed_hosts}

    def resolve_site(self, url: str) -> SiteTarget:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").rstrip(".").lower()
        if parsed.scheme != "https" or not hostname or hostname not in self._allowed_hosts:
            raise ValueError("URL is not an approved SharePoint tenant URL")

        segments = [unquote(segment) for segment in parsed.path.split("/") if segment]
        if len(segments) < 2 or segments[0].lower() not in {"sites", "teams"}:
            raise ValueError("URL must identify a SharePoint /sites/ or /teams/ site")
        site_path = f"/{segments[0]}/{segments[1]}"
        response = self._graph.request(
            "GET",
            f"/sites/{hostname}:{quote(site_path, safe='/')}",
            params={"$select": "id,webUrl,displayName"},
        )
        record = response.json()
        if not isinstance(record, dict):
            raise ValueError("Graph returned an invalid site record")
        site_id = str(record["id"])

        drives = list(
            self._graph.iter_collection(
                f"/sites/{quote(site_id, safe=',')}/drives",
                params={"$select": "id,name,driveType,webUrl"},
            )
        )
        document_drives = [
            drive for drive in drives if drive.get("driveType") == "documentLibrary"
        ]
        if not document_drives:
            raise FileNotFoundError("site has no document library")
        requested_library = segments[2].casefold() if len(segments) > 2 else None
        url_selected = next(
            (
                candidate
                for candidate in document_drives
                if requested_library
                and unquote(urlparse(str(candidate.get("webUrl", ""))).path)
                .rstrip("/")
                .rsplit("/", 1)[-1]
                .casefold()
                == requested_library
            ),
            None,
        )
        drive = next(
            (
                candidate
                for candidate in document_drives
                if str(candidate.get("name", "")).casefold() == "documents"
            ),
            document_drives[0],
        )
        if url_selected is not None:
            drive = url_selected
        return SiteTarget(
            site_id=site_id,
            drive_id=str(drive["id"]),
            web_url=str(record["webUrl"]),
            display_name=str(record.get("displayName") or segments[1]),
        )

    def resolve_path(self, drive_id: str, relative_path: str) -> DriveItem:
        drive = quote(drive_id, safe="")
        root = self._graph.request("GET", f"/drives/{drive}/root").json()
        if not isinstance(root, dict):
            raise ValueError("Graph returned an invalid drive root")
        current = DriveItem.from_graph(root)
        for segment in (
            part for part in relative_path.strip("/").split("/") if part
        ):
            match = next(
                (
                    child
                    for child in self.iter_children(drive_id, current.id)
                    if child.name.casefold() == segment.casefold()
                ),
                None,
            )
            if match is None:
                raise FileNotFoundError(
                    f"SharePoint path segment {segment!r} was not found"
                )
            current = match
        return current

    def iter_children(self, drive_id: str, item_id: str) -> Iterator[DriveItem]:
        path = (
            f"/drives/{quote(drive_id, safe='')}/items/"
            f"{quote(item_id, safe='')}/children"
        )
        for record in self._graph.iter_collection(
            path,
            params={"$select": "id,name,folder,file,size,webUrl"},
        ):
            yield DriveItem.from_graph(record)

    def download(
        self,
        drive_id: str,
        item_id: str,
    ) -> Iterator[bytes]:
        response = self._graph.request(
            "GET",
            f"/drives/{quote(drive_id, safe='')}/items/"
            f"{quote(item_id, safe='')}/content",
            stream=True,
        )
        yield from response.iter_bytes()
