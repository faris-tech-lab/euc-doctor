from __future__ import annotations

import plistlib
from dataclasses import dataclass
from pathlib import Path

import psutil

from euc_doctor.models import ActionCategory, ActionDefinition, ActionResult, ActionType, ExecutionContext, Severity
from euc_doctor.utils import discover_paths, format_bytes, info_result, is_macos, path_size, skip_non_macos


@dataclass(frozen=True)
class AppSupportModule:
    slug: str
    display_name: str
    bundle_patterns: tuple[str, ...]
    process_names: tuple[str, ...]
    cache_patterns: tuple[str, ...] = ()
    data_patterns: tuple[str, ...] = ()
    log_patterns: tuple[str, ...] = ()
    support_summary: str = ""
    support_steps: tuple[str, ...] = ()
    sources: tuple[str, ...] = ()


def _discover(patterns: tuple[str, ...]) -> list[Path]:
    return discover_paths(patterns)


def _app_version(app_path: Path) -> str | None:
    info_path = app_path / "Contents" / "Info.plist"
    if not info_path.exists():
        return None
    try:
        with info_path.open("rb") as handle:
            info = plistlib.load(handle)
    except (OSError, plistlib.InvalidFileException):
        return None
    return info.get("CFBundleShortVersionString") or info.get("CFBundleVersion")


def _running_processes(process_names: tuple[str, ...]) -> list[str]:
    matches: list[str] = []
    needles = tuple(name.lower() for name in process_names)
    for proc in psutil.process_iter(["name"]):
        name = (proc.info.get("name") or "").lower()
        if not name:
            continue
        if any(needle in name for needle in needles):
            matches.append(proc.info["name"] or name)
    return sorted(set(matches))


def _summarize_paths(label: str, patterns: tuple[str, ...]) -> str:
    paths = _discover(patterns)
    if not paths:
        return f"{label}: not found"
    total = sum(path_size(path) for path in paths)
    return f"{label}: {format_bytes(total)} across {len(paths)} path(s)"


def _status_handler(module: AppSupportModule):
    def handler(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
        if not is_macos():
            return skip_non_macos(action)
        app_paths = _discover(module.bundle_patterns)
        if not app_paths:
            return ActionResult(
                action.action_id,
                action.category,
                action.action_type,
                action.name,
                Severity.SKIPPED,
                f"{module.display_name} was not detected in common app locations.",
            )

        details = []
        for app_path in app_paths:
            version = _app_version(app_path)
            details.append(f"App: {app_path}")
            if version:
                details.append(f"Version: {version}")
        running = _running_processes(module.process_names)
        details.append(f"Running processes: {', '.join(running) if running else 'not running'}")
        if module.cache_patterns:
            details.append(_summarize_paths("Cache footprint", module.cache_patterns))
        if module.data_patterns:
            details.append(_summarize_paths("Data footprint", module.data_patterns))
        if module.log_patterns:
            details.append(_summarize_paths("Log footprint", module.log_patterns))

        return ActionResult(
            action.action_id,
            action.category,
            action.action_type,
            action.name,
            Severity.INFO,
            f"Collected installation and support footprint details for {module.display_name}.",
            "\n".join(details),
        )

    return handler


def _logs_handler(module: AppSupportModule):
    def handler(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
        if not is_macos():
            return skip_non_macos(action)
        log_paths = _discover(module.log_patterns)
        if not log_paths:
            return ActionResult(
                action.action_id,
                action.category,
                action.action_type,
                action.name,
                Severity.SKIPPED,
                f"No common {module.display_name} log paths were found.",
            )

        files: list[Path] = []
        for path in log_paths:
            if path.is_file():
                files.append(path)
            elif path.is_dir():
                files.extend(child for child in path.rglob("*") if child.is_file())
        files = sorted(files, key=lambda item: item.stat().st_mtime, reverse=True)[:10]
        if not files:
            return ActionResult(
                action.action_id,
                action.category,
                action.action_type,
                action.name,
                Severity.SKIPPED,
                f"{module.display_name} log locations exist but no files were found.",
            )

        detail = "\n".join(f"{file_path} ({format_bytes(file_path.stat().st_size)})" for file_path in files)
        return ActionResult(
            action.action_id,
            action.category,
            action.action_type,
            action.name,
            Severity.INFO,
            f"Collected recent {module.display_name} log file locations.",
            detail,
        )

    return handler


def _playbook_handler(module: AppSupportModule):
    def handler(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
        lines = [module.support_summary, ""]
        lines.append("Suggested support flow:")
        for step in module.support_steps:
            lines.append(f"- {step}")
        if module.sources:
            lines.append("")
            lines.append("Official sources:")
            for source in module.sources:
                lines.append(f"- {source}")
        return info_result(action, f"Loaded the {module.display_name} support playbook.", "\n".join(lines).strip())

    return handler


def build_actions(module: AppSupportModule) -> list[ActionDefinition]:
    return [
        ActionDefinition(
            f"apps.{module.slug}_status",
            ActionCategory.APPS,
            ActionType.DIAGNOSE,
            f"{module.display_name} status",
            f"Collect install, runtime, cache, and support-footprint details for {module.display_name}.",
            _status_handler(module),
        ),
        ActionDefinition(
            f"apps.{module.slug}_logs",
            ActionCategory.APPS,
            ActionType.DIAGNOSE,
            f"{module.display_name} logs",
            f"List recent log files or crash artifacts associated with {module.display_name}.",
            _logs_handler(module),
        ),
        ActionDefinition(
            f"apps.{module.slug}_playbook",
            ActionCategory.APPS,
            ActionType.INFO,
            f"{module.display_name} support playbook",
            f"Show a researched first-line support workflow for {module.display_name}.",
            _playbook_handler(module),
        ),
    ]
