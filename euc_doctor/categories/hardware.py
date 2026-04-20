from __future__ import annotations

from euc_doctor.models import ActionCategory, ActionDefinition, ActionResult, ActionType, ExecutionContext, Severity
from euc_doctor.utils import info_result, is_macos, run_cmd, skip_non_macos


def _summary(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["system_profiler", "SPHardwareDataType"], timeout=25)
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected hardware summary.", result.stdout[:1800] or result.stderr or None)


def _battery(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["system_profiler", "SPPowerDataType"], timeout=25)
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected battery and power data.", result.stdout[:1800] or result.stderr or None)


def _displays(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["system_profiler", "SPDisplaysDataType"], timeout=25)
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected display configuration.", result.stdout[:1800] or result.stderr or None)


def _bluetooth(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["system_profiler", "SPBluetoothDataType"], timeout=25)
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected Bluetooth data.", result.stdout[:1800] or result.stderr or None)


def _warranty(_, action: ActionDefinition):
    return info_result(action, "Manual-only warranty lookup.", "Use the Mac serial number from the hardware summary with Apple's coverage site or your asset management system.")


ACTIONS = [
    ActionDefinition("hw.summary", ActionCategory.HARDWARE, ActionType.DIAGNOSE, "Hardware summary", "Show the current Mac hardware summary.", _summary),
    ActionDefinition("hw.battery", ActionCategory.HARDWARE, ActionType.DIAGNOSE, "Battery health", "Collect battery health and power data.", _battery),
    ActionDefinition("hw.displays", ActionCategory.HARDWARE, ActionType.DIAGNOSE, "Displays", "Collect display configuration and connected monitor details.", _displays),
    ActionDefinition("hw.bluetooth", ActionCategory.HARDWARE, ActionType.DIAGNOSE, "Bluetooth devices", "Collect Bluetooth status and paired device information.", _bluetooth),
    ActionDefinition("hw.warranty", ActionCategory.HARDWARE, ActionType.INFO, "Warranty lookup playbook", "Explain how to verify device coverage using the serial number.", _warranty),
]
