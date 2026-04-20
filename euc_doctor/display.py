from __future__ import annotations

import shutil
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from euc_doctor.models import ActionDefinition, Severity, ToolkitRun
from euc_doctor.utils import current_host, current_platform_label, current_user, format_bytes

console = Console()

SEVERITY_STYLES = {
    Severity.OK: ("OK", "green"),
    Severity.WARN: ("WARN", "yellow"),
    Severity.FAIL: ("FAIL", "red"),
    Severity.FIXED: ("FIXED", "bright_green"),
    Severity.SKIPPED: ("SKIP", "grey70"),
    Severity.INFO: ("INFO", "cyan"),
}


def build_banner() -> Panel:
    usage = shutil.disk_usage(Path.home())
    free_display = format_bytes(usage.free)
    percent_free = int((usage.free / usage.total) * 100) if usage.total else 0
    content = Text()
    content.append("EUC Doctor  v0.1.0\n", style="bold bright_cyan")
    content.append(f"{current_platform_label()}  |  {current_user()}@{current_host()}\n", style="white")
    content.append(f"Disk Free: {free_display} ({percent_free}%)", style="grey70")
    return Panel(content, border_style="bright_cyan")


def clear_screen() -> None:
    console.clear()


def _shorten(text: str, limit: int = 72) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def render_category_overview(category_rows: list[tuple[str, str, int]], clear_first: bool = False) -> None:
    if clear_first:
        clear_screen()
    table = Table(title="Categories", header_style="bold bright_cyan", expand=True)
    table.add_column("Category", style="bold white", ratio=3)
    table.add_column("Slug", style="cyan", ratio=2)
    table.add_column("Actions", justify="right", ratio=1)
    for label, slug, count in category_rows:
        table.add_row(label, slug, str(count))
    console.print(build_banner())
    console.print(table)


def render_action_catalog(actions: list[ActionDefinition], category_label: str | None = None, clear_first: bool = False) -> None:
    if clear_first:
        clear_screen()
    title = f"{category_label} Actions" if category_label else "Available Actions"
    table = Table(title=title, header_style="bold bright_cyan", expand=True)
    table.add_column("ID", style="bold white")
    table.add_column("Type", width=9)
    if category_label is None:
        table.add_column("Category", ratio=2)
    table.add_column("Name", ratio=3)
    table.add_column("Description", ratio=4)
    for action in actions:
        row = [action.action_id, action.action_type.value]
        if category_label is None:
            row.append(action.category.label)
        row.extend([action.name, _shorten(action.description)])
        table.add_row(*row)
    console.print(build_banner())
    console.print(table)


def render_confirmation(action: ActionDefinition) -> None:
    table = Table(title=f"Confirm {action.name}", header_style="bold bright_cyan")
    table.add_column("Field", style="bold white")
    table.add_column("Value")
    table.add_row("Action", action.name)
    table.add_row("Type", action.action_type.value)
    table.add_row("Category", action.category.label)
    table.add_row("Description", action.description)
    table.add_row("Requires admin", "yes" if action.requires_admin else "no")
    table.add_row("Touches", "\n".join(action.touches) if action.touches else "No predefined paths")
    console.print(table)


def render_results(run: ToolkitRun) -> None:
    table = Table(title=f"Results for {run.target}", header_style="bold bright_cyan")
    table.add_column("Status")
    table.add_column("Action", style="bold white")
    table.add_column("Message")
    table.add_column("Freed")
    for result in run.results:
        label, style = SEVERITY_STYLES[result.severity]
        table.add_row(
            f"[{style}]{label}[/{style}]",
            result.name,
            result.message,
            format_bytes(result.bytes_freed),
        )
    summary = Table(show_header=False, box=None)
    summary.add_row("Total actions", str(run.total))
    summary.add_row("Bytes freed", format_bytes(run.bytes_freed))
    summary.add_row("Needs restart", str(run.requires_restart_count))
    summary.add_row("Dry run", "yes" if run.dry_run else "no")
    console.print(build_banner())
    console.print(table)
    console.print(Panel(summary, title="Summary", border_style="bright_cyan"))


def render_history(entries: list[dict]) -> None:
    table = Table(title="Recent History", header_style="bold bright_cyan")
    table.add_column("Timestamp", style="bold white")
    table.add_column("Target")
    table.add_column("Action")
    table.add_column("Status")
    table.add_column("Message")
    for entry in entries:
        result = entry["result"]
        table.add_row(entry["timestamp"], entry["target"], result["action_id"], result["severity"], result["message"])
    console.print(build_banner())
    console.print(table)
