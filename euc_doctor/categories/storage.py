from __future__ import annotations

import shutil
from pathlib import Path

from euc_doctor.models import ActionCategory, ActionDefinition, ActionResult, ActionType, ExecutionContext, Severity
from euc_doctor.utils import clear_paths, format_bytes, is_macos, path_size, skip_non_macos


def _storage_overview(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    usage = shutil.disk_usage(Path.home())
    percent_used = int((usage.used / usage.total) * 100) if usage.total else 0
    severity = Severity.WARN if percent_used >= 85 else Severity.OK
    return ActionResult(
        action.action_id,
        action.category,
        action.action_type,
        action.name,
        severity,
        f"Disk used: {format_bytes(usage.used)} of {format_bytes(usage.total)} ({percent_used}%).",
        f"Free: {format_bytes(usage.free)}",
    )


def _largest_dirs(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    home = Path.home()
    candidates = []
    for child in home.iterdir():
        if child.is_dir():
            candidates.append((child, path_size(child)))
    top = sorted(candidates, key=lambda item: item[1], reverse=True)[:8]
    detail = "\n".join(f"{item[0].name}: {format_bytes(item[1])}" for item in top) if top else "No directories found."
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO, "Calculated the largest top-level home directories.", detail)


def _downloads(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    downloads = Path.home() / "Downloads"
    if not downloads.exists():
        return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.SKIPPED, "Downloads folder was not found.")
    files = sorted((item for item in downloads.iterdir()), key=lambda item: item.stat().st_mtime)[:10]
    detail = "\n".join(file.name for file in files) if files else "Downloads is empty."
    return ActionResult(
        action.action_id,
        action.category,
        action.action_type,
        action.name,
        Severity.INFO,
        f"Downloads uses {format_bytes(path_size(downloads))}.",
        detail,
    )


def _trash(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    trash = Path.home() / ".Trash"
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO, f"Trash currently uses {format_bytes(path_size(trash))}.", str(trash))


def _empty_trash(ctx: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    return clear_paths(ctx, action, ["~/.Trash/*"], "Emptied user Trash.")


ACTIONS = [
    ActionDefinition("storage.overview", ActionCategory.STORAGE, ActionType.DIAGNOSE, "Disk usage overview", "Show total, used, and free disk capacity for the current user volume.", _storage_overview),
    ActionDefinition("storage.large_dirs", ActionCategory.STORAGE, ActionType.DIAGNOSE, "Largest home directories", "Estimate the largest top-level directories in the current home folder.", _largest_dirs),
    ActionDefinition("storage.downloads", ActionCategory.STORAGE, ActionType.DIAGNOSE, "Downloads folder summary", "Show total size for Downloads and list some of the oldest entries.", _downloads),
    ActionDefinition("storage.trash", ActionCategory.STORAGE, ActionType.DIAGNOSE, "Trash size", "Show the current size of the user Trash directory.", _trash),
    ActionDefinition("storage.trash_empty", ActionCategory.STORAGE, ActionType.FIX, "Empty user Trash", "Remove files currently stored in the user's Trash.", _empty_trash, touches=("~/.Trash/*",)),
]
