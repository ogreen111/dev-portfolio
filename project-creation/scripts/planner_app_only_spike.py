"""Exercise Planner app-only writes in a temporary Microsoft 365 group."""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote

import requests
from dotenv import load_dotenv
from rfp_automation.graph_auth import load_auth_from_env
from rfp_automation.graph_cloud import graph_base


def request(
    method: str,
    path: str,
    *,
    token: str,
    body: object | None = None,
    headers: dict[str, str] | None = None,
) -> requests.Response:
    merged_headers = {"Authorization": f"Bearer {token}"}
    if headers:
        merged_headers.update(headers)
    return requests.request(
        method,
        f"{graph_base()}{path}",
        headers=merged_headers,
        json=body,
        timeout=30,
    )


def require(response: requests.Response, expected: int, operation: str) -> dict:
    if response.status_code != expected:
        try:
            detail = response.json().get("error", {})
        except requests.JSONDecodeError:
            detail = {"message": response.text[:300]}
        raise RuntimeError(
            f"{operation} failed with {response.status_code}: "
            f"{detail.get('code', '')} {detail.get('message', '')}"
        )
    return response.json() if response.content else {}


def _find_group_id_by_nickname(token: str, nickname: str, *, attempts: int = 5) -> str | None:
    """Recover the group id when the create call's response was lost to a
    timeout or parse failure, so cleanup can still find and delete it.

    Retries because a just-created group can be briefly invisible to
    directory-object filter queries (replication lag); a single lookup
    could otherwise misreport "never created" and skip cleanup.
    """
    filter_expr = quote(f"mailNickname eq '{nickname}'", safe="")
    path = f"/groups?$filter={filter_expr}&$select=id"
    for attempt in range(attempts):
        try:
            response = request(
                "GET",
                path,
                token=token,
                headers={"ConsistencyLevel": "eventual"},
            )
        except requests.RequestException:
            response = None
        if response is not None and response.status_code == 200:
            try:
                values = response.json().get("value", [])
            except (requests.JSONDecodeError, AttributeError):
                values = []
            if values:
                return str(values[0]["id"])
        elif response is not None and response.status_code not in {429, 502, 503, 504}:
            return None
        if attempt + 1 < attempts:
            time.sleep(3)
    return None


def run(owner_upn: str) -> dict[str, object]:
    token = load_auth_from_env().get_access_token()
    stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    run_id = uuid.uuid4().hex[:8]
    display_name = f"SSI Project Creation App-Only Spike {stamp}-{run_id}"
    nickname = f"ssi-project-creation-spike-{stamp}-{run_id}"
    group_id: str | None = None
    evidence: dict[str, object] = {"display_name": display_name}

    try:
        owner = require(
            request(
                "GET",
                f"/users/{quote(owner_upn)}?$select=id,userPrincipalName",
                token=token,
            ),
            200,
            "resolve owner",
        )
        owner_ref = f"{graph_base()}/users/{owner['id']}"
        group = require(
            request(
                "POST",
                "/groups",
                token=token,
                body={
                    "displayName": display_name,
                    "description": "Temporary app-only Planner capability spike; safe to delete.",
                    "groupTypes": ["Unified"],
                    "mailEnabled": True,
                    "mailNickname": nickname,
                    "securityEnabled": False,
                    "owners@odata.bind": [owner_ref],
                    "members@odata.bind": [owner_ref],
                },
            ),
            201,
            "create Microsoft 365 group",
        )
        group_id = group["id"]
        evidence["group_created"] = True

        plan_response: requests.Response | None = None
        for _ in range(12):
            plan_response = request(
                "POST",
                "/planner/plans",
                token=token,
                body={
                    "container": {
                        "url": f"{graph_base()}/groups/{group_id}",
                    },
                    "title": display_name,
                },
            )
            if plan_response.status_code == 201:
                break
            if plan_response.status_code not in {400, 404}:
                break
            time.sleep(10)
        assert plan_response is not None
        plan = require(plan_response, 201, "create Planner plan")
        evidence["plan_created"] = True

        bucket = require(
            request(
                "POST",
                "/planner/buckets",
                token=token,
                body={
                    "name": "Planning",
                    "planId": plan["id"],
                    "orderHint": " !",
                },
            ),
            201,
            "create Planning bucket",
        )
        evidence["bucket_created"] = True

        require(
            request(
                "POST",
                "/planner/tasks",
                token=token,
                body={
                    "planId": plan["id"],
                    "bucketId": bucket["id"],
                    "title": "App-only submittal card spike",
                },
            ),
            201,
            "create unassigned Planner task",
        )
        evidence["unassigned_task_created"] = True
        return evidence
    finally:
        if group_id is None:
            group_id = _find_group_id_by_nickname(token, nickname)
        if group_id is not None:
            primary_error = sys.exc_info()[1]
            cleanup: requests.Response | None = None
            cleanup_error: requests.RequestException | None = None
            for _ in range(15):
                try:
                    cleanup = request("DELETE", f"/groups/{group_id}", token=token)
                    cleanup_error = None
                except requests.RequestException as exc:
                    cleanup_error = exc
                    time.sleep(2)
                    continue
                if cleanup.status_code == 204:
                    break
                if cleanup.status_code not in {404, 429, 502, 503, 504}:
                    break
                time.sleep(2)
            cleanup_status = cleanup.status_code if cleanup is not None else None
            evidence["group_cleanup_status"] = cleanup_status
            if cleanup_status != 204:
                detail = (
                    f"transport error: {cleanup_error}"
                    if cleanup_error is not None
                    else f"HTTP {cleanup_status}"
                )
                message = f"temporary group cleanup failed with {detail}"
                if primary_error is not None:
                    primary_error.add_note(message)
                else:
                    raise RuntimeError(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--owner", default="ogreen@spectrumsi.com")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        parser.error("--execute is required because this creates temporary tenant resources")
    load_dotenv(args.env_file)
    print(json.dumps(run(args.owner), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
