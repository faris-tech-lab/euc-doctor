from __future__ import annotations

from .common import AppSupportModule

MODULE = AppSupportModule(
    slug="adobe_cc",
    display_name="Adobe Creative Cloud",
    bundle_patterns=(
        "/Applications/Utilities/Adobe Creative Cloud/ACC/Creative Cloud.app",
        "/Applications/Adobe Creative Cloud/ACC/Creative Cloud.app",
    ),
    process_names=("Creative Cloud", "CCXProcess", "Core Sync"),
    cache_patterns=(
        "~/Library/Caches/Adobe",
        "~/Library/Application Support/Adobe/Common/Media Cache Files",
    ),
    data_patterns=(
        "~/Library/Application Support/Adobe",
        "~/Library/Application Support/Adobe/OOBE",
        "~/Library/Application Support/Adobe/AAMUpdater",
    ),
    log_patterns=(
        "~/Library/Logs/Adobe",
    ),
    support_summary="Adobe Creative Cloud is a common Mac support target because sign-in, licensing, install state, and media cache issues can block creative workflows quickly.",
    support_steps=(
        "Separate app launch problems from Creative Cloud licensing or Apps tab problems before deleting shared Adobe data.",
        "Adobe documents OOBE and AAMUpdater cleanup for some Creative Cloud desktop app download and Apps tab issues.",
        "For installer failures, collect Adobe logs before using the Cleaner Tool or reinstalling.",
        "If only one Adobe app is affected, keep the troubleshooting scoped to that app before resetting broader Creative Cloud state.",
    ),
    sources=(
        "Adobe HelpX: https://helpx.adobe.com/creative-cloud/kb/cc-apps-download-install-update.html",
        "Adobe HelpX: https://helpx.adobe.com/creative-cloud/kb/creative-cloud-desktop-app-launch-fails.html",
    ),
)
