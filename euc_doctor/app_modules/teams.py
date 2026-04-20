from __future__ import annotations

from .common import AppSupportModule

MODULE = AppSupportModule(
    slug="teams",
    display_name="Microsoft Teams",
    bundle_patterns=("/Applications/Microsoft Teams.app", "/Applications/Microsoft Teams classic.app"),
    process_names=("Teams", "Microsoft Teams"),
    cache_patterns=(
        "~/Library/Containers/com.microsoft.teams2/Data/Library/Caches",
        "~/Library/Caches/com.microsoft.teams*",
        "~/Library/Application Support/Microsoft/Teams/Cache",
    ),
    data_patterns=(
        "~/Library/Application Support/Microsoft/Teams",
        "~/Library/Containers/com.microsoft.teams2",
    ),
    log_patterns=(
        "~/Library/Logs/Microsoft Teams",
        "~/Library/Application Support/Microsoft/Teams/logs",
    ),
    support_summary="Teams is a high-frequency support app on managed Macs because it mixes identity, cache, media, notifications, and device permissions.",
    support_steps=(
        "Quit Teams fully before cache or state troubleshooting.",
        "If behavior looks corrupted, clear the Teams cache and relaunch; Microsoft notes the first restart can take longer while the cache rebuilds.",
        "For sign-in issues, compare tenant/account state and capture the exact error before resetting local data.",
        "For call issues, verify camera, microphone, speaker, and screen-recording permissions in macOS Privacy & Security.",
    ),
    sources=(
        "Microsoft Learn: https://learn.microsoft.com/en-us/microsoftteams/troubleshoot/teams-administration/clear-teams-cache",
    ),
)
