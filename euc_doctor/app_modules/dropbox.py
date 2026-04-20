from __future__ import annotations

from .common import AppSupportModule

MODULE = AppSupportModule(
    slug="dropbox",
    display_name="Dropbox",
    bundle_patterns=("/Applications/Dropbox.app",),
    process_names=("Dropbox",),
    cache_patterns=(
        "~/Library/Caches/com.getdropbox.dropbox",
    ),
    data_patterns=(
        "~/Library/Application Support/Dropbox",
        "~/Dropbox",
    ),
    log_patterns=(
        "~/Library/Application Support/Dropbox/logs",
        "~/Library/Logs/Dropbox",
    ),
    support_summary="Dropbox is still a common Mac support app because sync state, Finder integration, file-provider behavior, and account confusion create frequent tickets.",
    support_steps=(
        "Start with sync status and whether the app is running in the menu bar before touching local state.",
        "If sync is stuck, Dropbox recommends checking network state, account selection, file names, date and time, and whether files are actually inside the Dropbox folder.",
        "If Finder badges or sync icons are missing, compare Dropbox against other Finder-integrated apps because extension conflicts can affect icon overlays.",
        "Use reinstall or account relink only after basic sync and local app-state checks fail.",
    ),
    sources=(
        "Dropbox Help: https://help.dropbox.com/en-en/sync/files-not-syncing",
        "Dropbox Help: https://help.dropbox.com/sync/check-sync-status",
        "Dropbox Help: https://help.dropbox.com/installs/badge-issues",
    ),
)
