from __future__ import annotations

from pathlib import Path

from euc_doctor.models import ActionCategory, ActionDefinition, ActionResult, ActionType, ExecutionContext, Severity
from euc_doctor.utils import info_result, is_macos, run_cmd, skip_non_macos


def _detect_agents() -> dict[str, str]:
    candidates = {
        "Jamf": ["pgrep", "-fl", "jamf"],
        "Kandji": ["pgrep", "-fl", "Kandji"],
        "Mosyle": ["pgrep", "-fl", "Mosyle"],
        "Workspace ONE": ["pgrep", "-fl", "Hub"],
    }
    detected: dict[str, str] = {}
    for label, command in candidates.items():
        result = run_cmd(command)
        if result.ok and result.stdout:
            detected[label] = result.stdout
    return detected


def _profiles_status(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["profiles", "status", "-type", "enrollment"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected MDM enrollment status.", result.stdout or result.stderr or None)


def _profiles_list(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["profiles", "list"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected installed profiles.", result.stdout[:1500] or result.stderr or None)


def _agent(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    detected = _detect_agents()
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if detected else Severity.WARN, ", ".join(detected) if detected else "No common MDM agent process was detected.")


def _dep(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    status = run_cmd(["profiles", "status", "-type", "enrollment"])
    show = run_cmd(["profiles", "show", "-type", "enrollment"])
    detail = "\n\n".join(part for part in [status.stdout[:900], show.stdout[:900]] if part)
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if status.ok or show.ok else Severity.WARN, "Collected automated device enrollment details.", detail or status.stderr or show.stderr or None)


def _agent_detail(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    detected = _detect_agents()
    if not detected:
        return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.WARN, "No supported MDM agent processes were detected.")
    lines = []
    for label, detail in detected.items():
        lines.append(f"{label}\n{detail}")
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO, "Collected process details for detected MDM agents.", "\n\n".join(lines))


def _daemons(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    mdmclient = run_cmd(["pgrep", "-fl", "mdmclient"])
    apsd = run_cmd(["pgrep", "-fl", "apsd"])
    detail = "\n\n".join(
        part
        for part in [
            f"mdmclient:\n{mdmclient.stdout}" if mdmclient.stdout else "",
            f"apsd:\n{apsd.stdout}" if apsd.stdout else "",
        ]
        if part
    )
    severity = Severity.INFO if mdmclient.stdout or apsd.stdout else Severity.WARN
    return ActionResult(action.action_id, action.category, action.action_type, action.name, severity, "Collected core MDM and push daemon state.", detail or mdmclient.stderr or apsd.stderr or None)


def _logs(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(
        [
            "log",
            "show",
            "--style",
            "compact",
            "--last",
            "30m",
            "--predicate",
            'process == "mdmclient" OR process == "profiles"',
        ],
        timeout=25,
    )
    output = result.stdout[:1800] if result.stdout else result.stderr
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected recent MDM-related log lines.", output or None)


def _jamf_binary(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    version = run_cmd(["jamf", "version"])
    which = run_cmd(["which", "jamf"])
    if not version.ok and not which.ok:
        return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.SKIPPED, "Jamf binary was not detected on this Mac.")
    detail_parts = []
    if which.stdout:
        detail_parts.append(f"Binary: {which.stdout}")
    if version.stdout:
        detail_parts.append(version.stdout)
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO, "Collected Jamf binary details.", "\n".join(detail_parts) or version.stderr or which.stderr or None)


def _jamf_connection(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["jamf", "checkJSSConnection"], timeout=25)
    if result.returncode == 127:
        return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.SKIPPED, "Jamf binary was not detected on this Mac.")
    severity = Severity.OK if result.ok else Severity.WARN
    return ActionResult(action.action_id, action.category, action.action_type, action.name, severity, "Ran Jamf Pro server connectivity check.", result.stdout or result.stderr or None)


def _jamf_framework(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    framework_paths = [
        Path("/usr/local/jamf"),
        Path("/Library/Application Support/JAMF"),
        Path("/Library/LaunchDaemons/com.jamfsoftware.task.1.plist"),
    ]
    existing = [str(path) for path in framework_paths if path.exists()]
    severity = Severity.INFO if existing else Severity.WARN
    message = "Collected common Jamf framework paths." if existing else "No common Jamf framework paths were found."
    return ActionResult(action.action_id, action.category, action.action_type, action.name, severity, message, "\n".join(existing) if existing else None)


def _jamf_authchanger(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["authchanger", "-print"])
    if result.returncode == 127:
        return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.SKIPPED, "authchanger was not detected on this Mac.")
    severity = Severity.INFO if result.ok else Severity.WARN
    return ActionResult(action.action_id, action.category, action.action_type, action.name, severity, "Collected authchanger state.", result.stdout or result.stderr or None)


def _checkin(_, action: ActionDefinition):
    return info_result(action, "Kept as INFO first.", "Forced check-in depends on the MDM vendor and your org's agent tooling, so this stays guided rather than automatic.")


def _inventory(_, action: ActionDefinition):
    return info_result(action, "Kept as INFO first.", "Inventory updates differ by MDM vendor. Typical examples are `sudo jamf recon` or the vendor's equivalent inventory sync action.")


def _agent_restart(_, action: ActionDefinition):
    return info_result(action, "Kept as INFO first.", "Agent restart steps vary by vendor, launch daemon name, and org policy, so this remains a guided action rather than an automatic one.")


def _jamf_policy(_, action: ActionDefinition):
    return info_result(action, "Jamf policy sync stays guided for now.", "Typical first-line remediation is `sudo jamf policy -verbose` after confirming the Mac still has working Jamf framework and server connectivity.")


def _jamf_recon(_, action: ActionDefinition):
    return info_result(action, "Jamf inventory sync stays guided for now.", "Typical first-line remediation is `sudo jamf recon` after confirming enrollment, Jamf binary health, and network access to the Jamf Pro server.")


def _jamf_authchanger_playbook(_, action: ActionDefinition):
    return info_result(action, "Jamf Connect authchanger workflow loaded.", "Safer order of operations:\n- inspect current `authchanger -print` state\n- capture Jamf Connect config and state\n- if login-window state is wrong, use Jamf-documented authchanger reset guidance\n- verify with the org's expected Jamf Connect login configuration before rebooting")


ACTIONS = [
    ActionDefinition("mdm.enrollment", ActionCategory.MDM, ActionType.DIAGNOSE, "MDM enrollment status", "Check enrollment status using the macOS profiles tool.", _profiles_status),
    ActionDefinition("mdm.dep", ActionCategory.MDM, ActionType.DIAGNOSE, "Automated enrollment details", "Collect additional DEP or ADE enrollment details from the profiles tool.", _dep),
    ActionDefinition("mdm.profiles", ActionCategory.MDM, ActionType.DIAGNOSE, "MDM profiles", "List installed profiles that may have been pushed by MDM.", _profiles_list),
    ActionDefinition("mdm.agent", ActionCategory.MDM, ActionType.DIAGNOSE, "MDM agent detection", "Detect a few common MDM agent processes.", _agent),
    ActionDefinition("mdm.agent_detail", ActionCategory.MDM, ActionType.DIAGNOSE, "MDM agent details", "Show process details for the MDM agent that appears to be installed.", _agent_detail),
    ActionDefinition("mdm.daemons", ActionCategory.MDM, ActionType.DIAGNOSE, "MDM daemon state", "Check whether mdmclient and apsd appear to be running.", _daemons),
    ActionDefinition("mdm.jamf_binary", ActionCategory.MDM, ActionType.DIAGNOSE, "Jamf binary", "Check whether the Jamf binary exists and report its version.", _jamf_binary),
    ActionDefinition("mdm.jamf_connection", ActionCategory.MDM, ActionType.DIAGNOSE, "Jamf server connectivity", "Run Jamf's built-in server connectivity check.", _jamf_connection),
    ActionDefinition("mdm.jamf_framework", ActionCategory.MDM, ActionType.DIAGNOSE, "Jamf framework state", "Check for common Jamf management framework paths and artifacts.", _jamf_framework),
    ActionDefinition("mdm.jamf_authchanger", ActionCategory.MDM, ActionType.DIAGNOSE, "Jamf authchanger state", "Inspect current authchanger state for Jamf Connect login workflows.", _jamf_authchanger),
    ActionDefinition("mdm.logs", ActionCategory.MDM, ActionType.DIAGNOSE, "Recent MDM logs", "Show a short recent slice of mdmclient and profiles log activity.", _logs),
    ActionDefinition("mdm.agent_restart", ActionCategory.MDM, ActionType.INFO, "MDM agent restart playbook", "Explain why agent restart stays manual in this version.", _agent_restart, requires_admin=True),
    ActionDefinition("mdm.checkin", ActionCategory.MDM, ActionType.INFO, "MDM check-in playbook", "Explain why forced MDM check-in remains guided for now.", _checkin, requires_admin=True),
    ActionDefinition("mdm.inventory", ActionCategory.MDM, ActionType.INFO, "MDM inventory playbook", "Explain why inventory refresh remains guided for now.", _inventory, requires_admin=True),
    ActionDefinition("mdm.jamf_policy", ActionCategory.MDM, ActionType.INFO, "Jamf policy sync playbook", "Show the recommended first-line Jamf policy sync flow.", _jamf_policy, requires_admin=True),
    ActionDefinition("mdm.jamf_recon", ActionCategory.MDM, ActionType.INFO, "Jamf inventory sync playbook", "Show the recommended first-line Jamf inventory sync flow.", _jamf_recon, requires_admin=True),
    ActionDefinition("mdm.jamf_authchanger_playbook", ActionCategory.MDM, ActionType.INFO, "Jamf authchanger playbook", "Show a safer authchanger troubleshooting flow for Jamf Connect login issues.", _jamf_authchanger_playbook, requires_admin=True),
]
