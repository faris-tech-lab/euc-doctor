from __future__ import annotations

from .common import AppSupportModule

MODULE = AppSupportModule(
    slug="safari",
    display_name="Safari",
    bundle_patterns=("/Applications/Safari.app",),
    process_names=("Safari",),
    cache_patterns=(
        "~/Library/Caches/com.apple.Safari",
        "~/Library/Safari",
    ),
    data_patterns=(
        "~/Library/Safari",
    ),
    log_patterns=(
        "~/Library/Logs/DiagnosticReports/*Safari*",
    ),
    support_summary="Safari matters in Mac support because it is the built-in browser for captive portals, many authentication flows, and Apple-integrated privacy behaviors.",
    support_steps=(
        "For page-specific issues, first test in a private window to separate website data from browser configuration.",
        "Apple documents clearing history and website data as the built-in way to reset stale Safari web state.",
        "If Safari is crashing, capture Diagnostic Reports before deleting data so you keep evidence for escalation.",
        "Check whether content blockers, extensions, or private relay settings are affecting behavior before blaming the site.",
    ),
    sources=(
        "Apple Support: https://support.apple.com/guide/safari/clear-your-browsing-history-sfri47acf5d6/mac",
        "Apple Support: https://support.apple.com/guide/safari/manage-cookies-and-website-data-sfri11471/mac",
    ),
)
