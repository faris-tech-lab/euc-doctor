from __future__ import annotations

from .common import AppSupportModule

MODULE = AppSupportModule(
    slug="zoom",
    display_name="Zoom",
    bundle_patterns=("/Applications/zoom.us.app",),
    process_names=("zoom.us", "Zoom"),
    cache_patterns=(
        "~/Library/Application Support/zoom.us/data",
        "~/Library/Caches/us.zoom.xos",
    ),
    data_patterns=(
        "~/Library/Application Support/zoom.us",
    ),
    log_patterns=(
        "~/Library/Logs/zoom.us",
        "~/Library/Application Support/zoom.us/logs",
    ),
    support_summary="Zoom issues on Mac often come down to permissions, audio routing, virtual camera conflicts, or stale local state after updates.",
    support_steps=(
        "Verify camera, microphone, screen recording, and accessibility permissions in macOS before deeper reset work.",
        "If audio or video devices are missing, compare the device list in Zoom with the macOS Sound and Privacy settings.",
        "Reproduce the issue and collect Zoom logs before reinstalling, especially for crashing or meeting-join failures.",
        "Use a reinstall only after permissions and local logs point away from a simple configuration problem.",
    ),
    sources=(
        "Zoom Support: https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0065063",
        "Zoom Support: https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0061165",
    ),
)
