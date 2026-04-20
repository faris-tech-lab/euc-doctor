from __future__ import annotations

from .common import AppSupportModule

MODULE = AppSupportModule(
    slug="onedrive",
    display_name="OneDrive",
    bundle_patterns=("/Applications/OneDrive.app",),
    process_names=("OneDrive",),
    cache_patterns=(
        "~/Library/Caches/com.microsoft.OneDrive-mac",
    ),
    data_patterns=(
        "~/Library/Application Support/OneDrive",
        "~/Library/Containers/com.microsoft.OneDrive-mac",
    ),
    log_patterns=(
        "~/Library/Logs/OneDrive",
        "~/Library/Application Support/OneDrive/logs",
    ),
    support_summary="OneDrive is a major EUC support app because file sync, Files On-Demand, sign-in state, and macOS file-provider integration all create common tickets.",
    support_steps=(
        "Start with sync state, account state, and any Files On-Demand warnings before resetting the app.",
        "Microsoft documents a Mac reset flow inside the app bundle; use that instead of deleting synced content folders.",
        "Confirm whether the issue is one user, one library, or the whole OneDrive client before unlinking and relinking.",
        "Collect logs if sync errors persist after a reset so you retain tenant and item-level evidence.",
    ),
    sources=(
        "Microsoft Support: https://support.microsoft.com/en-us/office/reset-onedrive-34701e00-bf7b-42db-b960-84905399050c",
        "Microsoft Support: https://support.microsoft.com/en-us/office/fix-onedrive-sync-problems-0899b115-05f7-45ec-95b2-e4cc8c4670b2",
    ),
)
