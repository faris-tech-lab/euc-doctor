from __future__ import annotations

from .common import AppSupportModule

MODULE = AppSupportModule(
    slug="chrome",
    display_name="Google Chrome",
    bundle_patterns=("/Applications/Google Chrome.app",),
    process_names=("Google Chrome", "Chrome"),
    cache_patterns=(
        "~/Library/Caches/Google/Chrome",
        "~/Library/Application Support/Google/Chrome/Default/Cache",
    ),
    data_patterns=(
        "~/Library/Application Support/Google/Chrome",
    ),
    log_patterns=(
        "~/Library/Application Support/Google/Chrome/Crashpad",
        "~/Library/Logs/Google/Chrome",
    ),
    support_summary="Chrome is one of the most common browser support targets on managed Macs because SSO, extensions, profiles, cache, and policy can all break the user experience.",
    support_steps=(
        "Start by isolating whether the issue is browser-wide, profile-specific, or caused by an extension.",
        "For rendering, sign-in, or stale web-app behavior, clear cache or site data before resetting the whole profile.",
        "If the browser is managed, inspect policy or management state before telling users to reset settings.",
        "Use Chrome's built-in reset path only after confirming the issue is not tied to tenant policy, extension requirements, or a broken site.",
    ),
    sources=(
        "Google Chrome Help: https://support.google.com/chrome/",
        "Chrome Enterprise and Education Help: https://support.google.com/chrome/a/",
    ),
)
