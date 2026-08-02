# Planner App-Only Tenant Spike — 2026-07-29

## Decision

The existing `rfp-automation` certificate service principal can provision the
Planner resources required by Project Creation using app-only Microsoft Graph
authentication. Delegated sign-in is not required for the initial workflow.

## Tenant Evidence

The read-only preflight confirmed these relevant application roles:

- `Tasks.ReadWrite.All`
- `Group.ReadWrite.All`
- `Sites.Selected`
- `User.ReadBasic.All`

The template plan and its buckets were both readable with HTTP 200.

The isolated write spike then completed all of the following:

1. Created a temporary Microsoft 365 group with
   `ogreen@spectrumsi.com` as owner and member.
2. Created a basic Planner plan in that group.
3. Created a `Planning` bucket.
4. Created an unassigned task in that bucket.
5. Deleted the temporary group with HTTP 204.

The spike did not write to either example/template plan.

## Implementation Consequence

The application will use certificate-based app-only Graph access for group,
plan, bucket, task, and SharePoint operations. The operator remains the
application audit actor, while `ogreen@spectrumsi.com` is the initial Microsoft
365 group owner/member until per-user Microsoft identity is introduced.

Microsoft documents `Tasks.ReadWrite.All` application permission for creating
[plans](https://learn.microsoft.com/en-us/graph/api/planner-post-plans?view=graph-rest-1.0),
[buckets](https://learn.microsoft.com/en-us/graph/api/planner-post-buckets?view=graph-rest-1.0),
and [tasks](https://learn.microsoft.com/en-us/graph/api/planner-post-tasks?view=graph-rest-1.0).

## Repeatability and Cleanup

Run the guarded spike only when tenant verification is needed:

```bash
.venv/bin/python scripts/planner_app_only_spike.py \
  --env-file ../rfp-automation/.env \
  --owner ogreen@spectrumsi.com \
  --execute
```

The script uses a timestamped temporary group and deletes it in a `finally`
block. Cleanup retries HTTP 404 during initial directory propagation.
