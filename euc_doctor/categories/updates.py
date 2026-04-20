from __future__ import annotations

from euc_doctor.models import ActionCategory, ActionDefinition, ActionResult, ActionType, ExecutionContext, Severity
from euc_doctor.utils import info_result, is_macos, run_cmd, skip_non_macos


def _macos(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    version = run_cmd(["sw_vers"])
    updates = run_cmd(["softwareupdate", "--list"], timeout=20)
    detail = (version.stdout or "") + "\n\n" + (updates.stdout or updates.stderr or "")
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if version.ok else Severity.WARN, "Collected macOS version and pending update info.", detail.strip())


def _cli_tools(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["xcode-select", "-p"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.OK if result.ok else Severity.WARN, "Collected Xcode Command Line Tools path.", result.stdout or result.stderr or None)


def _brew(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    result = run_cmd(["brew", "outdated"], timeout=20)
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.SKIPPED, "Collected outdated Homebrew packages." if result.ok else "Homebrew not found or unavailable.", result.stdout or result.stderr or None)


def _install(_, action: ActionDefinition):
    return info_result(action, "Kept as INFO first.", "Installing updates is intentionally not automated in this version because timing, reboots, and corporate patch policy vary widely.")


ACTIONS = [
    ActionDefinition("updates.macos", ActionCategory.UPDATES, ActionType.DIAGNOSE, "macOS updates", "Show the current macOS version and pending updates.", _macos),
    ActionDefinition("updates.cli_tools", ActionCategory.UPDATES, ActionType.DIAGNOSE, "Xcode CLI tools", "Check whether Xcode Command Line Tools are installed.", _cli_tools),
    ActionDefinition("updates.brew_outdated", ActionCategory.UPDATES, ActionType.DIAGNOSE, "Outdated Homebrew packages", "List outdated Homebrew packages if brew is installed.", _brew),
    ActionDefinition("updates.install", ActionCategory.UPDATES, ActionType.INFO, "Update install playbook", "Explain why update installation remains a guided manual action.", _install, requires_admin=True),
]
