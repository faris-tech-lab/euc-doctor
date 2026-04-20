from __future__ import annotations

from euc_doctor.models import ActionCategory, ActionDefinition, ActionResult, ActionType, ExecutionContext, Severity
from euc_doctor.utils import clear_paths, discover_paths, format_bytes, is_macos, path_size, run_cmd, skip_non_macos

CACHE_GROUPS = {
    "Teams (classic)": ["~/Library/Caches/com.microsoft.teams*", "~/Library/Application Support/Microsoft/Teams/Cache"],
    "Teams (new)": ["~/Library/Containers/com.microsoft.teams2/Data/Library/Caches"],
    "Outlook": ["~/Library/Caches/com.microsoft.Outlook", "~/Library/Group Containers/UBF8T346G9.Office/Outlook/Outlook 15 Profiles"],
    "Slack": ["~/Library/Application Support/Slack/Cache", "~/Library/Application Support/Slack/Code Cache"],
    "Chrome": ["~/Library/Caches/Google/Chrome", "~/Library/Application Support/Google/Chrome/Default/Cache"],
    "VS Code": ["~/Library/Application Support/Code/Cache", "~/Library/Application Support/Code/CachedData"],
    "Cursor": ["~/Library/Application Support/Cursor/Cache", "~/Library/Application Support/Cursor/CachedData"],
    "Safari": ["~/Library/Caches/com.apple.Safari"],
}


def _cache_sizes(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    rows = []
    total = 0
    for label, patterns in CACHE_GROUPS.items():
        paths = discover_paths(patterns)
        size = sum(path_size(path) for path in paths)
        total += size
        rows.append(f"{label}: {format_bytes(size)}")
    severity = Severity.WARN if total > 1_000_000_000 else Severity.OK
    return ActionResult(
        action.action_id,
        action.category,
        action.action_type,
        action.name,
        severity,
        f"Known app caches total {format_bytes(total)}.",
        "\n".join(rows) if rows else "No known cache paths were found.",
    )


def _system_cache_size(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    user_cache = discover_paths(["~/Library/Caches"])
    total = sum(path_size(path) for path in user_cache)
    severity = Severity.WARN if total > 5_000_000_000 else Severity.INFO
    return ActionResult(
        action.action_id,
        action.category,
        action.action_type,
        action.name,
        severity,
        f"User Library caches use {format_bytes(total)}.",
        "\n".join(str(path) for path in user_cache) if user_cache else "No ~/Library/Caches directory was found.",
    )


def _flush_dns(ctx: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    if ctx.dry_run:
        return ActionResult(
            action.action_id,
            action.category,
            action.action_type,
            action.name,
            Severity.INFO,
            "Dry run: would flush local DNS caches.",
            "sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder",
            requires_admin=True,
        )
    result = run_cmd("sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder", shell=True)
    severity = Severity.FIXED if result.ok else Severity.FAIL
    return ActionResult(
        action.action_id,
        action.category,
        action.action_type,
        action.name,
        severity,
        "Flushed macOS DNS caches." if result.ok else "Failed to flush DNS caches.",
        result.stdout or result.stderr or None,
        requires_admin=True,
    )


def _clear_group(ctx: ExecutionContext, action: ActionDefinition, group_name: str, success_message: str) -> ActionResult:
    return clear_paths(ctx, action, CACHE_GROUPS[group_name], success_message, requires_restart=True)


def _clear_teams(ctx: ExecutionContext, action: ActionDefinition) -> ActionResult:
    return _clear_group(ctx, action, "Teams (new)", "Cleared new Teams cache.")


def _clear_outlook(ctx: ExecutionContext, action: ActionDefinition) -> ActionResult:
    return _clear_group(ctx, action, "Outlook", "Cleared Outlook cache and local profile data.")


def _clear_slack(ctx: ExecutionContext, action: ActionDefinition) -> ActionResult:
    return _clear_group(ctx, action, "Slack", "Cleared Slack cache.")


def _clear_chrome(ctx: ExecutionContext, action: ActionDefinition) -> ActionResult:
    return _clear_group(ctx, action, "Chrome", "Cleared Chrome cache.")


def _clear_vscode(ctx: ExecutionContext, action: ActionDefinition) -> ActionResult:
    return _clear_group(ctx, action, "VS Code", "Cleared VS Code cache.")


def _clear_cursor(ctx: ExecutionContext, action: ActionDefinition) -> ActionResult:
    return _clear_group(ctx, action, "Cursor", "Cleared Cursor cache.")


def _clear_safari(ctx: ExecutionContext, action: ActionDefinition) -> ActionResult:
    return _clear_group(ctx, action, "Safari", "Cleared Safari cache.")


def _clear_all_known(ctx: ExecutionContext, action: ActionDefinition) -> ActionResult:
    patterns = [pattern for group in CACHE_GROUPS.values() for pattern in group]
    return clear_paths(ctx, action, patterns, "Cleared all known application caches.", requires_restart=True)


ACTIONS = [
    ActionDefinition("cache.sizes", ActionCategory.CACHE, ActionType.DIAGNOSE, "Show known cache sizes", "Summarize common app cache locations and their sizes.", _cache_sizes),
    ActionDefinition("cache.system_size", ActionCategory.CACHE, ActionType.DIAGNOSE, "User cache footprint", "Show the total size of the current user's Library cache directory.", _system_cache_size),
    ActionDefinition("cache.teams", ActionCategory.CACHE, ActionType.FIX, "Clear new Teams cache", "Remove common cache directories used by the new Microsoft Teams app.", _clear_teams, touches=tuple(CACHE_GROUPS["Teams (new)"])),
    ActionDefinition("cache.outlook", ActionCategory.CACHE, ActionType.FIX, "Clear Outlook cache", "Remove Outlook cache and local profile directories commonly involved in sync issues.", _clear_outlook, touches=tuple(CACHE_GROUPS["Outlook"])),
    ActionDefinition("cache.slack", ActionCategory.CACHE, ActionType.FIX, "Clear Slack cache", "Remove Slack cache and code cache directories from the user profile.", _clear_slack, touches=tuple(CACHE_GROUPS["Slack"])),
    ActionDefinition("cache.chrome", ActionCategory.CACHE, ActionType.FIX, "Clear Chrome cache", "Remove Chrome cache directories from the active user profile.", _clear_chrome, touches=tuple(CACHE_GROUPS["Chrome"])),
    ActionDefinition("cache.vscode", ActionCategory.CACHE, ActionType.FIX, "Clear VS Code cache", "Remove VS Code cache directories from the current user profile.", _clear_vscode, touches=tuple(CACHE_GROUPS["VS Code"])),
    ActionDefinition("cache.cursor", ActionCategory.CACHE, ActionType.FIX, "Clear Cursor cache", "Remove Cursor cache directories from the current user profile.", _clear_cursor, touches=tuple(CACHE_GROUPS["Cursor"])),
    ActionDefinition("cache.safari", ActionCategory.CACHE, ActionType.FIX, "Clear Safari cache", "Remove Safari cache directories from the current user profile.", _clear_safari, touches=tuple(CACHE_GROUPS["Safari"])),
    ActionDefinition("cache.all", ActionCategory.CACHE, ActionType.FIX, "Clear all known caches", "Remove all app cache locations currently modeled by the toolkit.", _clear_all_known, touches=tuple(pattern for group in CACHE_GROUPS.values() for pattern in group)),
    ActionDefinition("cache.dns", ActionCategory.CACHE, ActionType.FIX, "Flush DNS cache", "Flush the macOS DNS resolver cache and restart the responder.", _flush_dns, touches=("dscacheutil", "mDNSResponder"), requires_admin=True),
]
