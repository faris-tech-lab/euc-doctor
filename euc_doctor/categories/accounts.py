from __future__ import annotations

from euc_doctor.models import ActionCategory, ActionDefinition, ActionResult, ActionType, ExecutionContext, Severity
from euc_doctor.utils import current_user, info_result, is_macos, run_cmd, skip_non_macos


def _users(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["dscl", ".", "-list", "/Users"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected local user accounts.", result.stdout or result.stderr or None)


def _admin(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["dsmemberutil", "checkmembership", "-U", current_user(), "-G", "admin"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.OK if "is a member" in result.stdout else Severity.WARN, result.stdout or "Checked admin membership.")


def _keychain(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["security", "default-keychain"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected default keychain.", result.stdout or result.stderr or None)


def _keychain_reset(_, action: ActionDefinition):
    return info_result(action, "Kept as INFO first.", "Default keychain reset is intentionally manual because it can disrupt saved secrets, tokens, and enterprise authentication workflows.")


ACTIONS = [
    ActionDefinition("acct.list", ActionCategory.ACCOUNTS, ActionType.DIAGNOSE, "Local user accounts", "List local user accounts on the Mac.", _users),
    ActionDefinition("acct.admin_check", ActionCategory.ACCOUNTS, ActionType.DIAGNOSE, "Admin membership", "Check whether the current user is in the admin group.", _admin),
    ActionDefinition("acct.keychain_status", ActionCategory.ACCOUNTS, ActionType.DIAGNOSE, "Default keychain", "Show the current default keychain path.", _keychain),
    ActionDefinition("acct.keychain_reset", ActionCategory.ACCOUNTS, ActionType.INFO, "Keychain reset playbook", "Explain why keychain reset remains manual in this version.", _keychain_reset),
]
