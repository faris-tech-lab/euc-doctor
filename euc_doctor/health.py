from __future__ import annotations

from euc_doctor.models import ActionDefinition
from euc_doctor.registry import ACTION_INDEX

HEALTH_ACTION_IDS: tuple[str, ...] = (
    "storage.overview",
    "net.summary",
    "net.dns",
    "net.latency",
    "net.proxy",
    "perf.summary",
    "perf.uptime",
    "perf.cpu",
    "perf.memory",
    "sec.filevault",
    "sec.firewall",
    "updates.macos",
    "mdm.enrollment",
    "mdm.jamf_binary",
    "mdm.jamf_connection",
    "hw.summary",
    "hw.battery",
)


def health_actions() -> list[ActionDefinition]:
    return [ACTION_INDEX[action_id] for action_id in HEALTH_ACTION_IDS if action_id in ACTION_INDEX]
