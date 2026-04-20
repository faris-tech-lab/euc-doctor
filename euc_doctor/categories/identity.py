from __future__ import annotations

from euc_doctor.models import ActionCategory, ActionDefinition, ActionResult, ActionType, ExecutionContext, Severity
from euc_doctor.utils import info_result, is_macos, run_cmd, skip_non_macos


def _hostname(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    computer = run_cmd(["scutil", "--get", "ComputerName"])
    host = run_cmd(["scutil", "--get", "HostName"])
    local = run_cmd(["scutil", "--get", "LocalHostName"])
    detail = "\n".join(
        [
            f"ComputerName: {computer.stdout or '(unset)'}",
            f"HostName: {host.stdout or '(unset)'}",
            f"LocalHostName: {local.stdout or '(unset)'}",
        ]
    )
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO, "Collected hostname values.", detail)


def _ad_binding(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["dsconfigad", "-show"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected AD binding status.", result.stdout or result.stderr or None)


def _kerberos(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    result = run_cmd(["klist"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected Kerberos ticket state.", result.stdout or result.stderr or None)


def _profiles(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["profiles", "list"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected installed configuration profiles.", result.stdout[:1500] or result.stderr or None)


def _rebind(_, action: ActionDefinition):
    return info_result(action, "Kept as INFO first.", "AD rebind is intentionally manual here because it is tenant-specific, credential-sensitive, and easy to get wrong in a portfolio demo.")


ACTIONS = [
    ActionDefinition("id.hostname", ActionCategory.IDENTITY, ActionType.DIAGNOSE, "Hostname consistency", "Show ComputerName, HostName, and LocalHostName values.", _hostname),
    ActionDefinition("id.ad_binding", ActionCategory.IDENTITY, ActionType.DIAGNOSE, "AD binding status", "Inspect current Active Directory binding state.", _ad_binding),
    ActionDefinition("id.kerberos", ActionCategory.IDENTITY, ActionType.DIAGNOSE, "Kerberos tickets", "Inspect current Kerberos ticket status.", _kerberos),
    ActionDefinition("id.profiles", ActionCategory.IDENTITY, ActionType.DIAGNOSE, "Configuration profiles", "List installed configuration profiles.", _profiles),
    ActionDefinition("id.ad_rebind", ActionCategory.IDENTITY, ActionType.INFO, "AD rebind playbook", "Explain why AD rebind remains a guided manual action.", _rebind, requires_admin=True),
]
