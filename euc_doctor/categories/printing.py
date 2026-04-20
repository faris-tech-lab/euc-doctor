from __future__ import annotations

from euc_doctor.models import ActionCategory, ActionDefinition, ActionResult, ActionType, ExecutionContext, Severity
from euc_doctor.utils import info_result, is_macos, run_cmd, skip_non_macos


def _printers(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["lpstat", "-p"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected configured printers.", result.stdout or result.stderr or None)


def _status(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["lpstat", "-r"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected print system status.", result.stdout or result.stderr or None)


def _queue(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["lpstat", "-o"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected current print queue.", result.stdout or result.stderr or None)


def _reset(_, action: ActionDefinition):
    return info_result(action, "Kept as INFO first.", "Print system reset removes all printers and is intentionally manual in this version.")


ACTIONS = [
    ActionDefinition("print.list", ActionCategory.PRINTING, ActionType.DIAGNOSE, "Configured printers", "List printers known to CUPS on this Mac.", _printers),
    ActionDefinition("print.status", ActionCategory.PRINTING, ActionType.DIAGNOSE, "Print system status", "Check whether the local print system is running.", _status),
    ActionDefinition("print.queue", ActionCategory.PRINTING, ActionType.DIAGNOSE, "Print queue", "Show queued print jobs.", _queue),
    ActionDefinition("print.reset", ActionCategory.PRINTING, ActionType.INFO, "Print reset playbook", "Explain why print system reset remains manual in this version.", _reset, requires_admin=True),
]
