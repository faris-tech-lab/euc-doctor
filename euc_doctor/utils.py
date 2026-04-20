from __future__ import annotations

import getpass
import glob
import json
import os
import platform
import shutil
import socket
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

from euc_doctor.models import ActionDefinition, ActionResult, ActionType, ExecutionContext, Severity


def _default_app_dir() -> Path:
    if platform.system() == "Windows":
        return Path(os.getenv("APPDATA", str(Path.home() / "AppData" / "Roaming"))) / "euc-doctor"
    return Path.home() / ".euc-doctor"


APP_DIR = Path(os.getenv("EUC_DOCTOR_HOME", str(_default_app_dir())))
HISTORY_DIR = APP_DIR / "history"
BACKUP_DIR = APP_DIR / "backups"


@dataclass
class CommandResult:
    command: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def ensure_app_dirs() -> None:
    global APP_DIR, HISTORY_DIR, BACKUP_DIR
    try:
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        APP_DIR = Path.cwd() / ".euc-doctor"
        HISTORY_DIR = APP_DIR / "history"
        BACKUP_DIR = APP_DIR / "backups"
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_macos() -> bool:
    return platform.system() == "Darwin"


def current_platform_label() -> str:
    return f"{platform.system()} {platform.release()}"


def current_host() -> str:
    return socket.gethostname()


def current_user() -> str:
    return getpass.getuser()


def run_cmd(command: Sequence[str] | str, timeout: int = 15, shell: bool = False) -> CommandResult:
    rendered = command if isinstance(command, str) else " ".join(command)
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            shell=shell,
        )
    except FileNotFoundError as exc:
        return CommandResult(rendered, 127, "", str(exc))
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or "Command timed out."
        return CommandResult(rendered, 124, stdout, stderr)
    return CommandResult(rendered, completed.returncode, completed.stdout.strip(), completed.stderr.strip())


def format_bytes(value: int | None) -> str:
    if value is None:
        return "-"
    amount = float(value)
    units = ["B", "KB", "MB", "GB", "TB"]
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            return f"{amount:.1f} {unit}" if unit != "B" else f"{int(amount)} B"
        amount /= 1024
    return f"{value} B"


def path_size(path: Path) -> int:
    try:
        if path.is_file():
            return path.stat().st_size
        total = 0
        for child in path.rglob("*"):
            if child.is_file():
                total += child.stat().st_size
        return total
    except (FileNotFoundError, PermissionError, OSError):
        return 0


def discover_paths(patterns: Iterable[str]) -> list[Path]:
    found: list[Path] = []
    seen: set[str] = set()
    for pattern in patterns:
        expanded = os.path.expanduser(pattern)
        for match in glob.glob(expanded):
            candidate = Path(match)
            key = str(candidate.resolve()) if candidate.exists() else str(candidate)
            if key in seen:
                continue
            seen.add(key)
            found.append(candidate)
    return found


def clear_paths(
    ctx: ExecutionContext,
    action: ActionDefinition,
    patterns: Iterable[str],
    success_message: str,
    requires_restart: bool = False,
) -> ActionResult:
    paths = discover_paths(patterns)
    if not paths:
        return ActionResult(
            action_id=action.action_id,
            category=action.category,
            action_type=action.action_type,
            name=action.name,
            severity=Severity.SKIPPED,
            message="Nothing matched the known paths on this machine.",
            detail="No cache or file paths were found for this action.",
            requires_admin=action.requires_admin,
        )

    bytes_freed = sum(path_size(path) for path in paths)
    if ctx.dry_run:
        return ActionResult(
            action_id=action.action_id,
            category=action.category,
            action_type=action.action_type,
            name=action.name,
            severity=Severity.INFO,
            message=f"Dry run: would touch {len(paths)} path(s).",
            detail="\n".join(str(path) for path in paths),
            bytes_freed=bytes_freed,
            requires_restart=requires_restart,
            requires_admin=action.requires_admin,
            touched_paths=tuple(str(path) for path in paths),
        )

    for path in paths:
        try:
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
        except OSError as exc:
            return ActionResult(
                action_id=action.action_id,
                category=action.category,
                action_type=action.action_type,
                name=action.name,
                severity=Severity.FAIL,
                message=f"Failed while removing {path.name}.",
                detail=str(exc),
                bytes_freed=bytes_freed,
                requires_restart=requires_restart,
                requires_admin=action.requires_admin,
                touched_paths=tuple(str(item) for item in paths),
            )

    return ActionResult(
        action_id=action.action_id,
        category=action.category,
        action_type=action.action_type,
        name=action.name,
        severity=Severity.FIXED,
        message=success_message,
        detail="\n".join(str(path) for path in paths),
        bytes_freed=bytes_freed,
        requires_restart=requires_restart,
        requires_admin=action.requires_admin,
        touched_paths=tuple(str(path) for path in paths),
    )


def skip_non_macos(action: ActionDefinition, detail: str | None = None) -> ActionResult:
    return ActionResult(
        action_id=action.action_id,
        category=action.category,
        action_type=action.action_type,
        name=action.name,
        severity=Severity.SKIPPED,
        message="This action is currently implemented for macOS only.",
        detail=detail,
        requires_admin=action.requires_admin,
    )


def info_result(action: ActionDefinition, message: str, detail: str | None = None) -> ActionResult:
    return ActionResult(
        action_id=action.action_id,
        category=action.category,
        action_type=ActionType.INFO,
        name=action.name,
        severity=Severity.INFO,
        message=message,
        detail=detail,
        requires_admin=action.requires_admin,
        touched_paths=action.touches,
    )


def backup_path(path: Path, label: str) -> Path | None:
    ensure_app_dirs()
    if not path.exists():
        return None
    safe_label = label.replace(" ", "-").lower()
    destination = BACKUP_DIR / f"{safe_label}-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{path.name}"
    if path.is_dir():
        shutil.copytree(path, destination)
    else:
        shutil.copy2(path, destination)
    return destination


def write_history_entry(target: str, result: ActionResult, dry_run: bool) -> None:
    ensure_app_dirs()
    path = HISTORY_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    payload = {
        "timestamp": now_iso(),
        "target": target,
        "dry_run": dry_run,
        "result": result.to_dict(),
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


def read_history(limit: int = 20) -> list[dict]:
    ensure_app_dirs()
    entries: list[dict] = []
    for file_path in sorted(HISTORY_DIR.glob("*.jsonl"), reverse=True):
        with file_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                entries.append(json.loads(line))
                if len(entries) >= limit:
                    return entries
    return entries
