from __future__ import annotations

from .common import AppSupportModule

MODULE = AppSupportModule(
    slug="slack",
    display_name="Slack",
    bundle_patterns=("/Applications/Slack.app",),
    process_names=("Slack",),
    cache_patterns=(
        "~/Library/Application Support/Slack/Cache",
        "~/Library/Application Support/Slack/Code Cache",
        "~/Library/Application Support/Slack/GPUCache",
    ),
    data_patterns=(
        "~/Library/Application Support/Slack",
    ),
    log_patterns=(
        "~/Library/Application Support/Slack/logs",
    ),
    support_summary="Slack is a frequent support touchpoint for enterprise Macs because workspace loading, notifications, sign-in, and cache corruption all surface there quickly.",
    support_steps=(
        "For loading issues, use Slack's built-in Help > Troubleshooting > Clear Cache and Restart flow before deleting folders manually.",
        "If messages or notifications are stuck, test whether the problem is local state versus workspace-side behavior.",
        "If Slack keeps prompting on macOS, verify Keychain access because Slack stores account information there.",
        "For connection issues, gather Slack network logs after reproducing the problem if cache clearing does not help.",
    ),
    sources=(
        "Slack Help: https://slack.com/help/articles/205138367-Troubleshoot-connection-issues",
        "Slack Help: https://slack.com/help/articles/115003653183-Grant-Keychain-access-to-Slack",
    ),
)
