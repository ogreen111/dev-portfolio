#!/usr/bin/env bash
# scripts/migrate-project.sh <project-name>
#
# Moves one project from ~/Documents/dev/<name> to ~/dev/<name>, stops and
# repoints any LaunchAgents that reference the old path, repairs git
# worktrees, and verifies the result. Refuses to run if the repo isn't
# clean and fully pushed, or if iCloud is still mid-sync - both are exactly
# the conditions that caused a live revert during this migration's own
# planning session.
set -euo pipefail

if ((BASH_VERSINFO[0] < 4)); then
  echo "FATAL: this script needs bash >= 4 (associative arrays)." >&2
  echo "       macOS ships bash 3.2 at /bin/bash; install a newer one via" >&2
  echo "       'brew install bash' and make sure /opt/homebrew/bin precedes" >&2
  echo "       /usr/bin in PATH so 'env bash' picks it up." >&2
  exit 1
fi

PROJECT="${1:?usage: migrate-project.sh <project-name>}"
if [[ ! "$PROJECT" =~ ^[A-Za-z0-9._-]+$ ]] || [ "$PROJECT" = "." ] || [ "$PROJECT" = ".." ]; then
  echo "FATAL: '$PROJECT' is not a safe project name (letters, digits, '.', '_', '-' only; no '/' or '..')." >&2
  exit 1
fi
OLD="$HOME/Documents/dev/$PROJECT"
NEW="$HOME/dev/$PROJECT"

# If the script stops LaunchAgents and then dies partway through (a later
# mv/sed/bootstrap failing under set -e), make sure that's loud instead of
# silently leaving services down - loaded_labels is populated by the
# "Stopping LaunchAgents" step below.
loaded_labels=""
on_exit() {
  local rc=$?
  if [ "$rc" -ne 0 ] && [ -n "$loaded_labels" ]; then
    echo "" >&2
    echo "WARNING: script exiting (status $rc) after stopping LaunchAgents:$loaded_labels" >&2
    echo "         these were not confirmed reloaded - check/restart by hand, e.g.:" >&2
    for l in $loaded_labels; do
      echo "           launchctl bootstrap \"gui/$(id -u)\" \"$HOME/Library/LaunchAgents/$l.plist\"" >&2
    done
  fi
}
trap on_exit EXIT

# Project -> space-separated LaunchAgent labels. From the inventory in
# 00-inventory-and-preflight.md Step 6. Add new entries here as new
# LaunchAgent-backed projects are found; a project with no entry just
# skips this section (safe default).
declare -A LAUNCH_AGENTS=(
  [claude-sync]="com.ogreen.claude-sync com.ogreen.claude-sync.healthcheck com.ogreen.claude-sync.menubar"
  [rfp-automation]="com.rfpautomation.dashboard com.rfpautomation.dashboard-healthcheck com.rfpautomation.logrotate com.rfpautomation.portalchrome com.rfpautomation.plannerchrome com.rfpautomation.optimizeloop com.rfpautomation.sentryloop com.rfpautomation.watcher"
  [cert-manager]="com.ssi.cert-manager-frontend com.ssi.cert-manager-backend"
  [email-processor]="com.ssi.email-intake.webserver com.ssi.email-intake.watcher"
  [digital-twin]="com.ssi.digital-twin"
  [network-scanner]="com.ssi.network-scanner"
  [past-performance]="com.ssi.past-performance"
  [scribe]="com.ssi.scribe"
  [project-tracking]="com.ssi.project-tracking com.ssi.project-tracking-exec-report com.ssi.project-tracking-snapshot com.ssi.project-tracking-sage-prewarm"
  [scripts]="com.ogreen.dev-portfolio-refresh"
)

# Project -> extra in-repo files with a hardcoded absolute Documents/dev
# path beyond what the generic end-of-script grep can safely auto-fix.
# Currently just claude-memory-compiler's uv wrapper.
declare -A EXTRA_FIXUP_FILES=(
  [claude-memory-compiler]="bin/uvr.sh"
)

# Project -> relative path from $OLD to the directory that actually
# contains .git, for projects where the repo isn't at the project's own
# top level. Confirmed this session: digital-twin's repo lives at
# digital-twin/frcs-digital-twin (matches its LaunchAgent's WorkingDirectory).
# A project with no entry here is assumed to have .git at its own top level.
declare -A GIT_SUBDIR=(
  [digital-twin]="frcs-digital-twin"
)

GIT_DIR="$OLD/${GIT_SUBDIR[$PROJECT]:-.}"
NEW_GIT_DIR="$NEW/${GIT_SUBDIR[$PROJECT]:-.}"

echo "==> Preflight: $PROJECT"

[ -d "$OLD" ] || { echo "FATAL: $OLD does not exist"; exit 1; }
[ -e "$NEW" ] && { echo "FATAL: $NEW already exists - already migrated?"; exit 1; }

if [ -e "$GIT_DIR/.git" ]; then
  status_output=$(git -C "$GIT_DIR" status --short) || {
    echo "FATAL: 'git status' failed in $GIT_DIR - repository may be corrupt. Investigate before moving."
    exit 1
  }
  if [ -n "$status_output" ]; then
    echo "FATAL: $PROJECT has uncommitted changes. Commit or stash first."
    exit 1
  fi
  # Linked worktrees never got this same check - only the main worktree
  # above did. A dirty linked worktree isn't a data-loss risk (ditto below
  # copies the working tree byte for byte regardless of git status), but it
  # breaks this script's own stated contract ("refuses to run if the repo
  # isn't clean") for exactly the files it never looked at. Deliberately
  # unconditional (not nested under the origin/FORCE_NO_REMOTE branching
  # below) - cleanliness has nothing to do with whether a remote exists, so
  # FORCE_NO_REMOTE=1 (which is about skipping *push* verification) must
  # not also skip this. Uses git worktree list --porcelain + sed (not awk)
  # for the same worktree-path-with-spaces reason as the repair verification
  # further down ("Pocket Probe" is a real project name here) - captured
  # once here and reused below for the unpushed-HEAD check.
  worktree_list_output=$(git -C "$GIT_DIR" worktree list --porcelain) || {
    echo "FATAL: 'git worktree list' failed in $GIT_DIR - cannot verify worktree state." >&2
    exit 1
  }
  # An array, not a space-joined string split back apart with `tr ' ' '\n'`
  # like the branch-name lists elsewhere in this script use - branch names
  # can't contain spaces, but worktree paths are real filesystem paths and
  # can ("Pocket Probe" is a real project name here), so splitting on space
  # would garble a legitimate path into two bogus lines in the FATAL below.
  dirty_worktrees=()
  while IFS= read -r wt_path; do
    [ -z "$wt_path" ] && continue
    [ "$wt_path" = "$GIT_DIR" ] && continue
    wt_status=$(git -C "$wt_path" status --short 2>&1) || {
      echo "FATAL: 'git status' failed in linked worktree $wt_path:" >&2
      echo "$wt_status" | sed 's/^/    /' >&2
      exit 1
    }
    [ -n "$wt_status" ] && dirty_worktrees+=("$wt_path")
  done < <(printf '%s\n' "$worktree_list_output" | sed -n 's/^worktree //p')
  if [ "${#dirty_worktrees[@]}" -gt 0 ]; then
    echo "FATAL: $PROJECT has linked worktrees with uncommitted changes:" >&2
    printf '    %s\n' "${dirty_worktrees[@]}" >&2
    echo "       Commit or stash first, same as for the main worktree above." >&2
    exit 1
  fi
  branch=$(git -C "$GIT_DIR" branch --show-current)
  if ! git -C "$GIT_DIR" remote get-url origin >/dev/null 2>&1; then
    echo "FATAL: $PROJECT has no 'origin' remote configured, so push status cannot be verified."
    echo "       Confirm by hand that nothing here would be lost before re-running with"
    echo "       FORCE_NO_REMOTE=1 $0 $PROJECT to skip this check."
    [ "${FORCE_NO_REMOTE:-0}" = "1" ] || exit 1
    echo "  git: no remote (FORCE_NO_REMOTE=1 set, proceeding without push verification)"
  elif ! git -C "$GIT_DIR" fetch origin --quiet --prune; then
    echo "FATAL: 'git fetch origin' failed for $PROJECT, so push status cannot be verified against current origin state."
    echo "       Confirm by hand that nothing here would be lost before re-running with"
    echo "       FORCE_NO_REMOTE=1 $0 $PROJECT to skip this check."
    [ "${FORCE_NO_REMOTE:-0}" = "1" ] || exit 1
    echo "  git: fetch failed (FORCE_NO_REMOTE=1 set, proceeding with possibly stale push data)"
  else
    if ! git -C "$GIT_DIR" rev-parse --verify -q "origin/$branch" >/dev/null 2>&1; then
      echo "FATAL: $PROJECT's branch '$branch' does not exist on origin, so push status cannot be verified."
      echo "       Confirm by hand that nothing here would be lost before re-running with"
      echo "       FORCE_NO_REMOTE=1 $0 $PROJECT to skip this check."
      [ "${FORCE_NO_REMOTE:-0}" = "1" ] || exit 1
      echo "  git: origin/$branch does not exist (FORCE_NO_REMOTE=1 set, proceeding without push verification)"
    elif [ -n "$(git -C "$GIT_DIR" log "origin/$branch..$branch" --oneline 2>/dev/null)" ]; then
      echo "FATAL: $PROJECT has commits not on origin/$branch. Push first."
      exit 1
    else
      # The checked-out branch being clean doesn't mean the whole repo is
      # backed up: a different local branch can carry commits origin has
      # never seen. ditto below copies the entire .git object database
      # regardless, so nothing is actually lost by the move itself, but the
      # point of this preflight is real confidence that origin already has
      # a copy before anything is touched.
      branch_heads=$(git -C "$GIT_DIR" for-each-ref --format='%(refname:short)' refs/heads) || {
        echo "FATAL: could not list local branches in $GIT_DIR." >&2
        exit 1
      }
      # Checked per-branch against every origin/* ref (not just a
      # same-named one) via rev-list, not by requiring a same-named
      # origin/<branch> to exist first - a branch with no origin
      # counterpart at all is exactly the case this needs to catch, and a
      # branch whose commits already landed on origin under a different
      # name correctly stays unflagged.
      other_branches_unpushed=""
      while IFS= read -r b; do
        [ -z "$b" ] && continue
        [ "$b" = "$branch" ] && continue
        # Capture rev-list's own failure explicitly - piping straight into
        # [ -n "$(...)" ] would treat a rev-list error (corrupt object,
        # broken ref) the same as "no unpushed commits" and silently wave
        # the branch through instead of aborting on an unknown state.
        b_unpushed=$(git -C "$GIT_DIR" rev-list "$b" --not --remotes=origin 2>&1) || {
          echo "FATAL: could not compute unpushed commits for local branch '$b' in $GIT_DIR:" >&2
          echo "$b_unpushed" | sed 's/^/    /' >&2
          exit 1
        }
        if [ -n "$b_unpushed" ]; then
          other_branches_unpushed="$other_branches_unpushed $b"
        fi
      done < <(printf '%s\n' "$branch_heads")
      if [ -n "$other_branches_unpushed" ]; then
        echo "FATAL: $PROJECT has local branches with commits absent from every origin ref:" >&2
        echo "$other_branches_unpushed" | tr ' ' '\n' | sed '/^$/d;s/^/    /' >&2
        echo "       Push these first, or switch to and push each before re-running." >&2
        exit 1
      fi
      # A linked worktree checked out on a detached HEAD (routine for
      # background-task worktrees, e.g. this portfolio's own
      # .claude/worktrees/* - confirmed live on project-tracking's two)
      # carries a commit that lives ONLY on that worktree's HEAD, not under
      # any refs/heads entry, so the branch loop above can't see it. Check
      # every linked worktree's HEAD directly against every origin/* ref,
      # same test as above. Reuses worktree_list_output, captured
      # unconditionally near the top of this script (see the comment
      # there for why cleanliness and push-status are checked separately).
      # An array, same space-in-path reason as dirty_worktrees above.
      unpushed_worktrees=()
      while IFS= read -r wt_path; do
        [ -z "$wt_path" ] && continue
        [ "$wt_path" = "$GIT_DIR" ] && continue
        wt_head=$(git -C "$wt_path" rev-parse HEAD 2>&1) || {
          echo "FATAL: could not read HEAD for linked worktree $wt_path:" >&2
          echo "$wt_head" | sed 's/^/    /' >&2
          exit 1
        }
        wt_unpushed=$(git -C "$GIT_DIR" rev-list "$wt_head" --not --remotes=origin 2>&1) || {
          echo "FATAL: could not compute unpushed commits for linked worktree $wt_path (HEAD $wt_head):" >&2
          echo "$wt_unpushed" | sed 's/^/    /' >&2
          exit 1
        }
        [ -n "$wt_unpushed" ] && unpushed_worktrees+=("$wt_path")
      done < <(printf '%s\n' "$worktree_list_output" | sed -n 's/^worktree //p')
      if [ "${#unpushed_worktrees[@]}" -gt 0 ]; then
        echo "FATAL: $PROJECT has linked worktrees with a HEAD commit absent from every origin ref:" >&2
        printf '    %s\n' "${unpushed_worktrees[@]}" >&2
        echo "       Typically a detached-HEAD background-task worktree. Push (or discard) it," >&2
        echo "       or remove it with 'git worktree remove', before re-running." >&2
        exit 1
      fi
      # Local-only tags are just a warning, not a FATAL - unlike branches,
      # tags don't have an implied "should be pushed" workflow, so their
      # absence from origin isn't necessarily a problem worth blocking on.
      local_tags=$(git -C "$GIT_DIR" for-each-ref --format='%(refname:short)' refs/tags 2>/dev/null || true)
      if [ -n "$local_tags" ]; then
        remote_tags=$(git -C "$GIT_DIR" ls-remote --tags origin 2>/dev/null | sed -E 's#^[^[:space:]]+[[:space:]]+refs/tags/##; s/\^\{\}$//' || true)
        local_only_tags=""
        while IFS= read -r t; do
          [ -z "$t" ] && continue
          grep -Fxq "$t" <<<"$remote_tags" || local_only_tags="$local_only_tags $t"
        done <<<"$local_tags"
        if [ -n "$local_only_tags" ]; then
          echo "  WARNING: local-only tags not found on origin (not blocking - review/push manually):"
          echo "$local_only_tags" | tr ' ' '\n' | sed '/^$/d;s/^/    /'
        fi
      fi
      echo "  git: clean, fully pushed to origin/$branch"
    fi
  fi
else
  echo "  WARNING: $PROJECT has no .git at $GIT_DIR - no push-safety check possible, moving as plain files"
fi

icloud_status=$(brctl status com.apple.CloudDocs 2>&1)
# Herestrings (not `echo ... | grep`) on purpose: under pipefail, a downstream
# command that exits early after a match (grep -q, or head after grep -o) can
# SIGPIPE the upstream writer, making the pipeline report non-zero even though
# the match was found - which would silently skip these FATAL checks for
# exactly the large-output case they exist to catch.
icloud_states=$(grep -o "client:[a-z-]*" <<<"$icloud_status" || true)
if [ -z "$icloud_states" ]; then
  echo "FATAL: could not find any 'client:' state in 'brctl status' output - investigate before moving."
  exit 1
fi
# Check every reported client: occurrence, not just the first - 'brctl status'
# can report more than one, and only checking the first missed a later
# non-idle state (confirmed live on this machine: a first call showed
# client:idle while a later call on the same host showed client:needs-sync
# with unclean items under this very directory).
non_idle=$(grep -v '^client:idle$' <<<"$icloud_states" || true)
if [ -n "$non_idle" ]; then
  echo "FATAL: iCloud is not idle ($(echo "$non_idle" | head -1)). Wait for it to settle before moving files."
  exit 1
fi
if grep -q "Client Truth Unclean Items" <<<"$icloud_status"; then
  echo "FATAL: iCloud reports idle but still lists unclean items - it flipped back to"
  echo "       active mid-sync during this migration's own planning session even while"
  echo "       showing idle moments earlier. Wait longer and re-check, don't override."
  exit 1
fi
echo "  iCloud: idle, no unclean items"

echo "==> Stopping LaunchAgents for $PROJECT"
for label in ${LAUNCH_AGENTS[$PROJECT]:-}; do
  if launchctl print "gui/$(id -u)/$label" >/dev/null 2>&1; then
    launchctl bootout "gui/$(id -u)/$label"
    echo "  stopped $label"
    loaded_labels="$loaded_labels $label"
  else
    echo "  $label not loaded, skipping"
  fi
done

echo "==> Copying $OLD -> $NEW"
echo "    (ditto, not mv - plain mv/rename() deadlocks under iCloud's file-provider"
echo "    coordinator even when 'stat -f' reports \$OLD and ~/dev on the same device;"
echo "    confirmed live on this machine, hung indefinitely on a 38MB repo and a"
echo "    134GB plain-file tree alike. ditto copies via read/write syscalls - still"
echo "    APFS-clone fast - and never touches the coordinator.)"
mkdir -p "$HOME/dev"
ditto "$OLD" "$NEW"

echo "==> Verifying the copy before touching the source"
# Content-level, not just entry-count: a count match doesn't catch a file
# ditto copied with truncated/corrupted bytes but the same name. diff -rq
# reads both trees (cheap here since ditto clonefile()s on APFS, so both
# sides share physical blocks until either diverges) and reports any file
# that's missing, extra, or differs in content on either side.
diff_output=$(diff -rq "$OLD" "$NEW" 2>&1) || true
if [ -n "$diff_output" ]; then
  echo "FATAL: ditto copy differs from source:" >&2
  echo "$diff_output" | sed 's/^/    /' >&2
  echo "       Source left untouched at $OLD; the incomplete/differing copy at $NEW was NOT removed - investigate before retrying." >&2
  exit 1
fi
entry_count=$(find "$NEW" | wc -l | tr -d ' ')
if [ -e "$GIT_DIR/.git" ]; then
  old_head=$(git -C "$GIT_DIR" rev-parse HEAD)
  new_head=$(git -C "$NEW_GIT_DIR" rev-parse HEAD 2>&1) || {
    echo "FATAL: could not read HEAD from the copied repo at $NEW_GIT_DIR." >&2
    echo "       Source left untouched at $OLD - investigate before retrying." >&2
    exit 1
  }
  if [ "$old_head" != "$new_head" ]; then
    echo "FATAL: HEAD mismatch after ditto ($old_head in $OLD vs $new_head in $NEW)." >&2
    echo "       Source left untouched at $OLD - investigate before retrying." >&2
    exit 1
  fi
  echo "  verified: $entry_count entries byte-identical (diff -rq clean), HEAD $new_head matches source"
else
  echo "  verified: $entry_count entries byte-identical (diff -rq clean, not a git repo so no HEAD to compare)"
fi

# Repair worktrees BEFORE removing $OLD, not after: a linked worktree's
# .git file and the main repo's worktrees/<name>/gitdir file point at each
# other by absolute path, and "git worktree repair" needs both sides
# reachable to relocate them. Doing this while $OLD still exists is the
# exact sequence verified end to end this session (niagara-llm, 3 linked
# worktrees); running it after deleting $OLD is untested and risks
# leaving a linked worktree permanently broken with no fallback copy left
# to recover from.
if [ -e "$NEW_GIT_DIR/.git" ]; then
  echo "==> Repairing git worktrees (no-op if none exist)"
  git -C "$NEW_GIT_DIR" worktree repair || true
  # worktree repair's own exit code is unreliable here: it prints a benign
  # "unable to locate repository ... .git.nosync" line (a known quirk of
  # this portfolio's .git -> .git.nosync symlink convention, unrelated to
  # repair success) and can exit non-zero even when every real linked
  # worktree was fixed correctly. Verify by actually opening each linked
  # worktree instead of trusting the exit code.
  #
  # Two things a naive check gets wrong, both because $OLD still exists at
  # this point (deliberately - see the comment above this block):
  #  - `git worktree list` can itself fail; piped into process substitution,
  #    that failure is silently swallowed by `set -e` and the loop below
  #    would just iterate zero times and report false success. Capture it
  #    into a variable first so a failure is caught explicitly.
  #  - a worktree whose repair silently failed still has its .git file
  #    pointing at $OLD's now-stale gitdir - and since $OLD still exists,
  #    `rev-parse HEAD` through that stale link succeeds anyway, masking
  #    the failure right up until $OLD is deleted below. Check that each
  #    worktree's resolved git-common-dir actually lives under $NEW, not
  #    just that some rev-parse call worked.
  worktree_list_output=$(git -C "$NEW_GIT_DIR" worktree list --porcelain) || {
    echo "FATAL: 'git worktree list' failed in $NEW_GIT_DIR - cannot verify worktrees." >&2
    echo "       Source left untouched at $OLD - investigate before retrying." >&2
    exit 1
  }
  broken_worktrees=""
  while IFS= read -r wt_path; do
    [ "$wt_path" = "$NEW_GIT_DIR" ] && continue
    common_dir=$(git -C "$wt_path" rev-parse --git-common-dir 2>&1) || { broken_worktrees="$broken_worktrees $wt_path"; continue; }
    case "$common_dir" in
      /*) common_dir_abs="$common_dir" ;;
      *) common_dir_abs="$wt_path/$common_dir" ;;
    esac
    common_dir_abs=$(cd "$common_dir_abs" 2>/dev/null && pwd -P) || { broken_worktrees="$broken_worktrees $wt_path"; continue; }
    case "$common_dir_abs" in
      "$NEW"/*|"$NEW") ;;
      *) broken_worktrees="$broken_worktrees $wt_path" ;;
    esac
  done < <(printf '%s\n' "$worktree_list_output" | sed -n 's/^worktree //p')
  if [ -n "$broken_worktrees" ]; then
    echo "FATAL: these linked worktrees are still broken after 'worktree repair'" >&2
    echo "       (still resolve outside $NEW):" >&2
    echo "$broken_worktrees" | tr ' ' '\n' | sed '/^$/d;s/^/    /' >&2
    echo "       Source left untouched at $OLD - investigate before retrying." >&2
    exit 1
  fi
  echo "  verified: all linked worktrees resolve under $NEW"
fi

# Final check immediately before deletion, right after everything above
# (worktree repair, LaunchAgent work below is what's left) that could have
# taken real wall-clock time since the first diff -rq: something else
# writing to $OLD in that window - iCloud resuming sync, a stray editor -
# would otherwise be silently lost. This doesn't close the race, it just
# shrinks it to the gap between this check and the rm call itself, which
# is as tight as achievable without real locking (not available here -
# it's exactly the coordinator that deadlocks and drove this script to
# ditto in the first place).
final_diff=$(diff -rq "$OLD" "$NEW" 2>&1) || true
if [ -n "$final_diff" ]; then
  echo "FATAL: $OLD changed since the earlier verification - not safe to delete:" >&2
  echo "$final_diff" | sed 's/^/    /' >&2
  echo "       Source left untouched at $OLD - investigate before retrying." >&2
  exit 1
fi

echo "==> Removing source $OLD"
rm -rf "$OLD"

# PROJECT is already restricted to [A-Za-z0-9._-]+ above; the only sed
# regex metacharacter that can appear in it is '.', which must be escaped
# so it matches a literal dot instead of "any character" in the patterns below.
PROJECT_SED_ESCAPED=$(printf '%s' "$PROJECT" | sed 's/\./\\./g')
OLD_PATH_ESCAPED="$HOME/Documents/dev/$PROJECT_SED_ESCAPED"
NEW_PATH_ESCAPED="$HOME/dev/$PROJECT_SED_ESCAPED"
# Boundary group after the project name so migrating "foo" doesn't also
# rewrite an unrelated "Documents/dev/foo-backup" or "Documents/dev/foo+old"
# sibling path (real macOS filenames can contain characters PROJECT itself
# never will, so the boundary can't just be "anything outside PROJECT's own
# charset" - that incorrectly treats a real filename character like '+' as
# a delimiter and clobbers an unrelated path). Enumerates the separators
# that can actually follow a path inside a plist's ProgramArguments/command
# string: /, quote, <, >, whitespace, a shell delimiter (; & | )), ':'
# (PATH-style EnvironmentVariables values like
# "PYTHONPATH=/old/project:/other" are a real LaunchAgent pattern in this
# portfolio), or end-of-line.
PATH_BOUNDARY_RE="[/'\"<>;&|):[:space:]]|\$"

echo "==> Repointing LaunchAgent plists for $PROJECT"
for label in ${LAUNCH_AGENTS[$PROJECT]:-}; do
  plist="$HOME/Library/LaunchAgents/$label.plist"
  [ -f "$plist" ] || { echo "  WARNING: $plist not found, skipping"; continue; }
  sed -i '' -E "s#($OLD_PATH_ESCAPED)($PATH_BOUNDARY_RE)#$NEW_PATH_ESCAPED\2#g" "$plist"
  # Verify the sed actually caught every occurrence instead of trusting a
  # zero exit code (sed exits 0 whether or not it matched anything) - a
  # boundary character this regex doesn't know about would otherwise leave
  # the plist silently pointed at the now-deleted $OLD.
  if grep -Eq "$OLD_PATH_ESCAPED($PATH_BOUNDARY_RE)" "$plist"; then
    echo "FATAL: $plist still references $HOME/Documents/dev/$PROJECT after repointing -" >&2
    echo "       the boundary regex didn't match every occurrence. Fix the plist by hand," >&2
    echo "       then bootstrap it (see WARNING above for LaunchAgents left stopped)." >&2
    exit 1
  fi
  echo "  repointed $plist"
done

echo "==> Fixing known in-repo absolute path references"
for f in ${EXTRA_FIXUP_FILES[$PROJECT]:-}; do
  target="$NEW/$f"
  [ -f "$target" ] || { echo "  WARNING: $target not found, skipping"; continue; }
  sed -i '' "s#$HOME/Documents/dev#$HOME/dev#g" "$target"
  echo "  fixed $target"
done

echo "==> Reloading LaunchAgents for $PROJECT"
# Only reload agents that were actually loaded before this script stopped them -
# an agent the user had deliberately disabled beforehand should stay disabled.
reload_failed=0
for label in $loaded_labels; do
  plist="$HOME/Library/LaunchAgents/$label.plist"
  if [ ! -f "$plist" ]; then
    echo "  WARNING: $plist not found - $label was stopped but could not be reloaded, check manually"
    reload_failed=1
    continue
  fi
  launchctl bootstrap "gui/$(id -u)" "$plist"
  echo "  reloaded $label"
done

echo "==> Verifying LaunchAgent state"
for label in ${LAUNCH_AGENTS[$PROJECT]:-}; do
  status=$(launchctl print "gui/$(id -u)/$label" 2>&1 | grep -m1 "state = " || echo "NOT RUNNING")
  echo "  $label: $status"
  # Real launchctl output is literally "state = not running" for a stopped
  # agent - a loose `*running*` match would wrongly treat that as running.
  case "$status" in
    *"state = running"*) ;;
    *) echo "  NOTE: $label is not in 'running' state - expected for interval/calendar-triggered agents between runs, otherwise verify manually" ;;
  esac
done

echo "==> Scanning the moved project for any remaining Documents/dev references"
remaining=$(grep -rl "Documents/dev" "$NEW" \
  --include="*.py" --include="*.md" --include="*.json" \
  --include="*.sh" --include="*.toml" --include="*.plist" \
  2>/dev/null || true)
if [ -n "$remaining" ]; then
  echo "  Found remaining references (review manually, may just be prose docs):"
  echo "$remaining" | sed 's/^/    /'
else
  echo "  none found"
fi

echo "==> Done. $PROJECT is now at $NEW"
if [ "$reload_failed" = "1" ]; then
  echo "FATAL: one or more previously-running LaunchAgents could not be reloaded (see WARNING above)." >&2
  exit 1
fi
