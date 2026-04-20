from __future__ import annotations

from pathlib import Path

from euc_doctor.models import ActionCategory, ActionDefinition, ActionResult, ActionType, ExecutionContext, Severity
from euc_doctor.utils import is_macos, run_cmd, skip_non_macos


def _filevault(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["fdesetup", "status"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.OK if "On" in result.stdout else Severity.WARN, "Collected FileVault status.", result.stdout or result.stderr or None)


def _firewall(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.OK if result.ok else Severity.WARN, "Collected firewall state.", result.stdout or result.stderr or None)


def _gatekeeper(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["spctl", "--status"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.OK if result.ok else Severity.WARN, "Collected Gatekeeper status.", result.stdout or result.stderr or None)


def _screen_lock(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["defaults", "read", "com.apple.screensaver", "askForPasswordDelay"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected screen lock delay setting.", result.stdout or result.stderr or None)


def _ssh_perms(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    ssh_dir = Path.home() / ".ssh"
    if not ssh_dir.exists():
        return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.SKIPPED, "No ~/.ssh directory was found.")
    mode = oct(ssh_dir.stat().st_mode)[-3:]
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.OK if mode == "700" else Severity.WARN, f"~/.ssh permissions look like {mode}.")


ACTIONS = [
    ActionDefinition("sec.filevault", ActionCategory.SECURITY, ActionType.DIAGNOSE, "FileVault status", "Check whether FileVault is enabled.", _filevault),
    ActionDefinition("sec.firewall", ActionCategory.SECURITY, ActionType.DIAGNOSE, "Firewall status", "Check the macOS application firewall state.", _firewall),
    ActionDefinition("sec.gatekeeper", ActionCategory.SECURITY, ActionType.DIAGNOSE, "Gatekeeper status", "Check Gatekeeper enforcement status.", _gatekeeper),
    ActionDefinition("sec.screen_lock", ActionCategory.SECURITY, ActionType.DIAGNOSE, "Screen lock delay", "Inspect the delay before password is required after sleep or screensaver.", _screen_lock),
    ActionDefinition("sec.ssh_perms", ActionCategory.SECURITY, ActionType.DIAGNOSE, "SSH directory permissions", "Check whether ~/.ssh is using a typical secure permission mode.", _ssh_perms),
]
