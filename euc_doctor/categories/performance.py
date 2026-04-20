from __future__ import annotations

from datetime import datetime

import psutil

from euc_doctor.models import ActionCategory, ActionDefinition, ActionResult, ActionType, ExecutionContext, Severity
from euc_doctor.utils import format_bytes


def _summary(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    memory = psutil.virtual_memory()
    uptime = datetime.fromtimestamp(psutil.boot_time())
    return ActionResult(
        action.action_id,
        action.category,
        action.action_type,
        action.name,
        Severity.OK,
        f"CPU cores: {psutil.cpu_count(logical=True)} | RAM used: {format_bytes(memory.used)} of {format_bytes(memory.total)}",
        f"Boot time: {uptime.isoformat(timespec='seconds')}",
    )


def _uptime(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    seconds = int(datetime.now().timestamp() - psutil.boot_time())
    days = seconds // 86400
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.WARN if days >= 14 else Severity.OK, f"System uptime is {days} day(s).")


def _cpu(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    usage = psutil.cpu_percent(interval=0.5)
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.WARN if usage >= 80 else Severity.OK, f"Current CPU usage is {usage:.1f}%.")


def _memory(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    memory = psutil.virtual_memory()
    return ActionResult(
        action.action_id,
        action.category,
        action.action_type,
        action.name,
        Severity.WARN if memory.percent >= 85 else Severity.OK,
        f"Memory pressure: {memory.percent:.1f}% used.",
        f"Available: {format_bytes(memory.available)}",
    )


def _top_processes(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    rows = []
    processes = sorted(
        psutil.process_iter(["name", "memory_info"]),
        key=lambda proc: proc.info["memory_info"].rss if proc.info["memory_info"] else 0,
        reverse=True,
    )[:8]
    for proc in processes:
        rss = proc.info["memory_info"].rss if proc.info["memory_info"] else 0
        rows.append(f"{proc.info['name'] or 'unknown'}: {format_bytes(rss)}")
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO, "Collected top memory-heavy processes.", "\n".join(rows))


ACTIONS = [
    ActionDefinition("perf.summary", ActionCategory.PERFORMANCE, ActionType.DIAGNOSE, "System summary", "Show CPU, RAM, and boot time details.", _summary),
    ActionDefinition("perf.uptime", ActionCategory.PERFORMANCE, ActionType.DIAGNOSE, "Uptime check", "Warn when the system has been up for a long time without a restart.", _uptime),
    ActionDefinition("perf.cpu", ActionCategory.PERFORMANCE, ActionType.DIAGNOSE, "CPU usage", "Measure current CPU load.", _cpu),
    ActionDefinition("perf.memory", ActionCategory.PERFORMANCE, ActionType.DIAGNOSE, "Memory usage", "Show current memory utilization and available RAM.", _memory),
    ActionDefinition("perf.top_processes", ActionCategory.PERFORMANCE, ActionType.DIAGNOSE, "Top processes", "List some of the most memory-heavy processes on the machine.", _top_processes),
]
