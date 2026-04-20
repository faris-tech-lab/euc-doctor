from __future__ import annotations

from euc_doctor.models import ActionCategory, ActionDefinition, ActionResult, ActionType, ExecutionContext, Severity
from euc_doctor.utils import info_result, is_macos, run_cmd, skip_non_macos


def _login_items(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["osascript", "-e", 'tell application "System Events" to get the name of every login item'])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected login item names.", result.stdout or result.stderr or None)


def _spotlight_status(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["mdutil", "-sa"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected Spotlight indexing status.", result.stdout or result.stderr or None)


def _restart_process(ctx: ExecutionContext, action: ActionDefinition, process_name: str, label: str) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    if ctx.dry_run:
        return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO, f"Dry run: would restart {process_name}.")
    result = run_cmd(["killall", process_name])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.FIXED if result.ok else Severity.FAIL, label, result.stdout or result.stderr or None)


def _finder_restart(ctx: ExecutionContext, action: ActionDefinition) -> ActionResult:
    return _restart_process(ctx, action, "Finder", "Restarted Finder.")


def _dock_restart(ctx: ExecutionContext, action: ActionDefinition) -> ActionResult:
    return _restart_process(ctx, action, "Dock", "Restarted Dock.")


def _show_hidden(_, action: ActionDefinition):
    return info_result(action, "Kept as INFO for now.", "Suggested commands:\ndefaults write com.apple.finder AppleShowAllFiles -bool true\nkillall Finder")


ACTIONS = [
    ActionDefinition("desktop.login_items", ActionCategory.DESKTOP, ActionType.DIAGNOSE, "Login items", "List configured login items for the current user.", _login_items),
    ActionDefinition("desktop.spotlight_status", ActionCategory.DESKTOP, ActionType.DIAGNOSE, "Spotlight status", "Show Spotlight indexing status for mounted volumes.", _spotlight_status),
    ActionDefinition("desktop.finder_restart", ActionCategory.DESKTOP, ActionType.FIX, "Restart Finder", "Restart Finder to recover from common UI glitches.", _finder_restart, touches=("Finder",)),
    ActionDefinition("desktop.dock_restart", ActionCategory.DESKTOP, ActionType.FIX, "Restart Dock", "Restart the Dock to recover from layout or animation issues.", _dock_restart, touches=("Dock",)),
    ActionDefinition("desktop.show_hidden", ActionCategory.DESKTOP, ActionType.INFO, "Show hidden files playbook", "Explain the safest way to toggle hidden files in Finder.", _show_hidden),
]
