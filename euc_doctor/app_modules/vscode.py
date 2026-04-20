from __future__ import annotations

from .common import AppSupportModule

MODULE = AppSupportModule(
    slug="vscode",
    display_name="Visual Studio Code",
    bundle_patterns=("/Applications/Visual Studio Code.app",),
    process_names=("Code", "Visual Studio Code"),
    cache_patterns=(
        "~/Library/Application Support/Code/Cache",
        "~/Library/Application Support/Code/CachedData",
    ),
    data_patterns=(
        "~/Library/Application Support/Code",
    ),
    log_patterns=(
        "~/Library/Application Support/Code/logs",
    ),
    support_summary="VS Code is a common support app on Mac fleets that support engineering, development, or technical power users because extension and profile issues often present as app issues.",
    support_steps=(
        "Use Extension Bisect before blaming the whole editor when problems start after an update or extension change.",
        "Collect VS Code logs and reproduce the issue before clearing profile data so you preserve evidence.",
        "Separate editor-core issues from language extension or terminal environment issues.",
        "If the app launches but behavior is broken, test with extensions disabled and a clean window first.",
    ),
    sources=(
        "VS Code Docs: https://code.visualstudio.com/docs/editor/extension-marketplace#_extension-bisect",
        "VS Code Docs: https://code.visualstudio.com/docs/supporting/troubleshoot",
    ),
)
