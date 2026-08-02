from typing import Any

import pytest

from project_creation.graph_client import GraphResponse
from project_creation.sharepoint import SharePointClient


def graph_response(body: object, chunks: tuple[bytes, ...] = ()) -> GraphResponse:
    return GraphResponse(status=200, headers={}, json_body=body, byte_chunks=chunks)


class StubGraph:
    def __init__(self) -> None:
        self.requests: list[tuple[str, str, dict[str, Any]]] = []
        self.responses: list[GraphResponse] = []
        self.collections: dict[str, list[dict[str, Any]]] = {}

    def request(self, method: str, path: str, **kwargs: Any) -> GraphResponse:
        self.requests.append((method, path, kwargs))
        return self.responses.pop(0)

    def iter_collection(
        self, path: str, **kwargs: Any
    ) -> list[dict[str, Any]]:
        self.requests.append(("GET_COLLECTION", path, kwargs))
        return self.collections[path]


def test_resolve_site_accepts_site_and_document_library_urls() -> None:
    graph = StubGraph()
    graph.responses = [
        graph_response(
            {
                "id": "tenant.sharepoint.com,site-guid,web-guid",
                "webUrl": "https://tenant.sharepoint.com/sites/Alpha",
                "displayName": "Alpha",
            }
        )
    ]
    graph.collections[
        "/sites/tenant.sharepoint.com,site-guid,web-guid/drives"
    ] = [
        {
            "id": "drive-1",
            "name": "Documents",
            "driveType": "documentLibrary",
            "webUrl": "https://tenant.sharepoint.com/sites/Alpha/Shared Documents",
        }
    ]
    client = SharePointClient(graph, allowed_hosts={"tenant.sharepoint.com"})

    site = client.resolve_site(
        "https://tenant.sharepoint.com/sites/Alpha/"
        "Shared%20Documents/Proposals/Tech/Cyber"
    )

    assert site.site_id == "tenant.sharepoint.com,site-guid,web-guid"
    assert site.drive_id == "drive-1"
    assert graph.requests[0][1] == "/sites/tenant.sharepoint.com:/sites/Alpha"


def test_resolve_site_selects_library_named_in_deep_url() -> None:
    graph = StubGraph()
    graph.responses = [
        graph_response(
            {
                "id": "site-id",
                "webUrl": "https://tenant.sharepoint.com/sites/Alpha",
                "displayName": "Alpha",
            }
        )
    ]
    graph.collections["/sites/site-id/drives"] = [
        {
            "id": "default",
            "name": "Documents",
            "driveType": "documentLibrary",
            "webUrl": "https://tenant.sharepoint.com/sites/Alpha/Shared Documents",
        },
        {
            "id": "cyber",
            "name": "Cyber Files",
            "driveType": "documentLibrary",
            "webUrl": "https://tenant.sharepoint.com/sites/Alpha/Cyber Files",
        },
    ]

    site = SharePointClient(
        graph, allowed_hosts={"tenant.sharepoint.com"}
    ).resolve_site("https://tenant.sharepoint.com/sites/Alpha/Cyber%20Files/Specs")

    assert site.drive_id == "cyber"


def test_resolve_site_with_no_library_in_url_uses_sites_default_drive() -> None:
    graph = StubGraph()
    graph.responses = [
        graph_response(
            {
                "id": "site-id",
                "webUrl": "https://tenant.sharepoint.com/sites/Alpha",
                "displayName": "Alpha",
            }
        ),
        graph_response(
            {
                "id": "default-drive",
                "name": "Dokumente",
                "driveType": "documentLibrary",
                "webUrl": "https://tenant.sharepoint.com/sites/Alpha/Dokumente",
            }
        ),
    ]

    site = SharePointClient(
        graph, allowed_hosts={"tenant.sharepoint.com"}
    ).resolve_site("https://tenant.sharepoint.com/sites/Alpha")

    assert site.drive_id == "default-drive"
    assert graph.requests[-1][:2] == ("GET", "/sites/site-id/drive")


def test_resolve_site_raises_when_requested_library_is_not_found() -> None:
    graph = StubGraph()
    graph.responses = [
        graph_response(
            {
                "id": "site-id",
                "webUrl": "https://tenant.sharepoint.com/sites/Alpha",
                "displayName": "Alpha",
            }
        )
    ]
    graph.collections["/sites/site-id/drives"] = [
        {
            "id": "default",
            "name": "Documents",
            "driveType": "documentLibrary",
            "webUrl": "https://tenant.sharepoint.com/sites/Alpha/Shared Documents",
        }
    ]

    with pytest.raises(FileNotFoundError):
        SharePointClient(
            graph, allowed_hosts={"tenant.sharepoint.com"}
        ).resolve_site("https://tenant.sharepoint.com/sites/Alpha/Nonexistent/Specs")


@pytest.mark.parametrize(
    "url",
    [
        "https://other.sharepoint.com/sites/Alpha",
        "not-a-url",
        "ftp://tenant.sharepoint.com/sites/Alpha",
    ],
)
def test_resolve_site_rejects_wrong_tenant_and_malformed_urls(url: str) -> None:
    with pytest.raises(ValueError):
        SharePointClient(StubGraph(), allowed_hosts={"tenant.sharepoint.com"}).resolve_site(
            url
        )


def test_resolve_path_walks_children_by_exact_name_and_reports_missing_segment() -> None:
    graph = StubGraph()
    graph.responses = [
        graph_response({"id": "root", "name": "root", "folder": {}}),
    ]
    graph.collections["/drives/drive/items/root/children"] = [
        {"id": "proposals", "name": "Proposals", "folder": {}}
    ]
    graph.collections["/drives/drive/items/proposals/children"] = [
        {"id": "tech", "name": "Tech", "folder": {}}
    ]
    client = SharePointClient(graph, allowed_hosts={"tenant.sharepoint.com"})

    item = client.resolve_path("drive", "Proposals/Tech")
    assert item.id == "tech"
    assert item.is_folder

    graph.responses = [graph_response({"id": "root", "name": "root", "folder": {}})]
    with pytest.raises(FileNotFoundError, match="Missing"):
        client.resolve_path("drive", "Proposals/Missing")


def test_resolve_path_preserves_literal_percent_escapes() -> None:
    graph = StubGraph()
    graph.responses = [
        graph_response({"id": "root", "name": "root", "folder": {}})
    ]
    graph.collections["/drives/drive/items/root/children"] = [
        {"id": "literal", "name": "Budget%20Draft", "folder": {}}
    ]

    item = SharePointClient(
        graph, allowed_hosts={"tenant.sharepoint.com"}
    ).resolve_path("drive", "Budget%20Draft")

    assert item.id == "literal"


def test_iter_children_and_download_preserve_folder_file_types_and_stream_bytes() -> None:
    graph = StubGraph()
    graph.collections["/drives/drive/items/parent/children"] = [
        {"id": "folder", "name": "System", "folder": {"childCount": 1}},
        {"id": "file", "name": "25 05 11.pdf", "file": {}, "size": 42},
    ]
    graph.responses = [
        graph_response(None, chunks=(b"first", b"second")),
    ]
    client = SharePointClient(graph, allowed_hosts={"tenant.sharepoint.com"})

    children = list(client.iter_children("drive", "parent"))
    assert [item.is_folder for item in children] == [True, False]
    assert b"".join(client.download("drive", "file")) == b"firstsecond"
    assert graph.requests[-1] == (
        "GET",
        "/drives/drive/items/file/content",
        {"stream": True},
    )
