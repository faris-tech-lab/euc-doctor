from __future__ import annotations

from .common import AppSupportModule

MODULE = AppSupportModule(
    slug="firefox",
    display_name="Firefox",
    bundle_patterns=("/Applications/Firefox.app",),
    process_names=("Firefox",),
    cache_patterns=(
        "~/Library/Caches/Firefox",
    ),
    data_patterns=(
        "~/Library/Application Support/Firefox",
    ),
    log_patterns=(
        "~/Library/Application Support/Firefox/Crash Reports",
    ),
    support_summary="Firefox is still common in enterprise support for security-conscious users, web compatibility testing, and fallback auth troubleshooting.",
    support_steps=(
        "Use Troubleshoot Mode or a clean profile check to separate add-on problems from browser-core problems.",
        "Mozilla's Refresh Firefox flow is a safer first reset than manually deleting the whole profile.",
        "If crashes are involved, gather crash reports before resetting the profile.",
        "For authentication issues, compare behavior against Safari or Chrome to see whether the problem is browser-specific or network-wide.",
    ),
    sources=(
        "Mozilla Support: https://support.mozilla.org/en-US/kb/refresh-firefox-reset-add-ons-and-settings",
        "Mozilla Support: https://support.mozilla.org/en-US/kb/diagnose-firefox-issues-using-troubleshoot-mode",
    ),
)
