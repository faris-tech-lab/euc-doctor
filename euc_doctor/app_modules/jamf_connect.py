from __future__ import annotations

from .common import AppSupportModule

MODULE = AppSupportModule(
    slug="jamf_connect",
    display_name="Jamf Connect",
    bundle_patterns=(
        "/Applications/Jamf Connect.app",
        "/Applications/Jamf Connect Login.app",
    ),
    process_names=("Jamf Connect", "Jamf Connect Login", "authchanger"),
    cache_patterns=(
        "~/Library/Application Support/JamfConnect",
        "~/Library/Logs/JamfConnect",
    ),
    data_patterns=(
        "~/Library/Preferences/com.jamf.connect.state.plist",
        "~/Library/Preferences/com.jamf.connect.plist",
        "~/Library/Preferences/com.jamf.connect.login.plist",
    ),
    log_patterns=(
        "~/Library/Logs/JamfConnect",
        "~/Library/Logs/Jamf Connect",
    ),
    support_summary="Jamf Connect is worth modeling directly because login-window behavior, identity-provider state, and authchanger configuration can block the entire Mac sign-in experience.",
    support_steps=(
        "Determine whether the problem is menu bar sync, login-window behavior, or account provisioning before changing authchanger state.",
        "Jamf documents `authchanger -reset` for restoring the default macOS login window and `authchanger -reset -JamfConnect` for enabling the Jamf Connect login window.",
        "Capture current authchanger state before changing it so you have evidence if the machine enters an unexpected login flow.",
        "If the issue is password sync or IdP-specific, collect Jamf Connect state and config details before escalation.",
    ),
    sources=(
        "Jamf Support: https://support.jamf.com/en/articles/11003602-authchanger-and-jamf-connect",
        "Jamf Developer Docs: https://developer.jamf.com/developer-guide/docs/jamf-connect",
    ),
)
