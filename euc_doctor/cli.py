from __future__ import annotations

from pathlib import Path

import typer

from euc_doctor import __version__
from euc_doctor.display import console, render_action_catalog, render_confirmation, render_history, render_results
from euc_doctor.formatters.jsonout import build_json
from euc_doctor.formatters.markdown import build_markdown
from euc_doctor.health import health_actions
from euc_doctor.interactive import launch_menu
from euc_doctor.models import ActionDefinition, ExecutionContext
from euc_doctor.registry import list_actions, resolve_target, run_actions, run_target
from euc_doctor.utils import read_history

app = typer.Typer(no_args_is_help=False, invoke_without_command=True, help="mac-first troubleshooting toolkit for support engineers.", rich_markup_mode="rich")


def _confirm(action: ActionDefinition) -> bool:
    render_confirmation(action)
    return typer.confirm("Proceed?", default=False)


def _context(dry_run: bool, yes: bool) -> ExecutionContext:
    return ExecutionContext(dry_run=dry_run, assume_yes=yes, confirmer=_confirm)


def _run_menu(dry_run: bool) -> None:
    while True:
        selection = launch_menu()
        if selection is None:
            return
        if selection.mode == "diagnose":
            render_results(run_target(selection.target, _context(dry_run=dry_run, yes=True), include_fixes=False))
        elif selection.mode == "health":
            render_results(run_actions("health", health_actions(), _context(dry_run=dry_run, yes=True)))
        else:
            render_results(run_target(selection.target, _context(dry_run=dry_run, yes=False)))
        if not typer.confirm("Go back to the menu?", default=True):
            return


@app.callback(invoke_without_command=True)
def entrypoint(ctx: typer.Context) -> None:
    """Launch the interactive menu when no subcommand is given."""
    if ctx.invoked_subcommand is None:
        _run_menu(False)


@app.command()
def list(category: str | None = typer.Option(None, "--category", "-c", help="Optional category filter.")) -> None:
    """List categories and actions."""
    actions = list_actions(category=category)
    category_label = actions[0].category.label if category and actions else None
    render_action_catalog(actions, category_label=category_label)


@app.command()
def diagnose(
    category: str | None = typer.Option(None, "--category", "-c", help="Run only one category."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview mode for consistency with fix runs."),
) -> None:
    """Run all read-only diagnose and info actions."""
    target = category or "all"
    render_results(run_target(target, _context(dry_run=dry_run, yes=True), include_fixes=False))


@app.command()
def health(dry_run: bool = typer.Option(False, "--dry-run", help="Preview mode for consistency with other commands.")) -> None:
    """Run a curated machine health check bundle."""
    render_results(run_actions("health", health_actions(), _context(dry_run=dry_run, yes=True)))


@app.command()
def run(
    target: str = typer.Argument(..., help="Category slug like cache, or a specific action id like cache.teams."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what a fix would touch without changing anything."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmations for fix actions."),
) -> None:
    """Run a category or a single action."""
    if not resolve_target(target):
        raise typer.BadParameter(f"Unknown category or action: {target}")
    render_results(run_target(target, _context(dry_run=dry_run, yes=yes)))


@app.command()
def report(
    category: str | None = typer.Option(None, "--category", "-c", help="Optional category filter."),
    format: str = typer.Option("markdown", "--format", "-f", help="markdown or json"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Destination file."),
) -> None:
    """Export a read-only report."""
    target = category or "all"
    run = run_target(target, _context(dry_run=False, yes=True), include_fixes=False)
    payload = build_markdown(run) if format.lower() == "markdown" else build_json(run)
    if output is None:
        output = Path("euc-doctor-report.md" if format.lower() == "markdown" else "euc-doctor-report.json")
    output.write_text(payload, encoding="utf-8")
    console.print(f"Wrote {format.lower()} report to {output}")


@app.command()
def history(limit: int = typer.Option(20, "--limit", "-n", help="Maximum history entries to display.")) -> None:
    """Show recent action history."""
    render_history(read_history(limit=limit))


@app.command()
def menu(dry_run: bool = typer.Option(False, "--dry-run", help="Preview fix actions without changing anything.")) -> None:
    """Launch the interactive menu."""
    _run_menu(dry_run)


@app.command()
def version() -> None:
    """Show the installed version."""
    console.print(__version__)


def run() -> None:
    app()


if __name__ == "__main__":
    run()
