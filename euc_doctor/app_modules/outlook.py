from __future__ import annotations

from .common import AppSupportModule

MODULE = AppSupportModule(
    slug="outlook",
    display_name="Outlook",
    bundle_patterns=("/Applications/Microsoft Outlook.app",),
    process_names=("Outlook", "Microsoft Outlook"),
    cache_patterns=(
        "~/Library/Caches/com.microsoft.Outlook",
        "~/Library/Group Containers/UBF8T346G9.Office/Outlook",
    ),
    data_patterns=(
        "~/Library/Group Containers/UBF8T346G9.Office/Outlook",
    ),
    log_patterns=(
        "~/Library/Containers/com.microsoft.Outlook/Data/Library/Logs",
        "~/Library/Logs/Outlook",
    ),
    support_summary="Outlook on Mac is a common ticket source because sync, identity, profile data, and local cache state can all affect mail behavior.",
    support_steps=(
        "Capture whether the issue is sync-only, auth-related, search-related, or tied to a single folder or account.",
        "Use Outlook's account reset flow first for server-synced data issues instead of deleting random local files.",
        "Warn that unsynced local-only data may be lost when resetting the account cache.",
        "If keychain prompts or auth loops appear, review Apple Keychain behavior before escalating to profile rebuild steps.",
    ),
    sources=(
        "Microsoft Support: https://support.microsoft.com/en-us/office/clear-the-cache-in-outlook-for-mac-ddd2d077-84d5-4d2a-8cda-59ca58a645aa",
        "Microsoft Support: https://support.microsoft.com/en-us/office/contact-support-within-outlook-for-mac-d0410177-8e65-4487-93f7-206a3a3d71a8",
    ),
)
