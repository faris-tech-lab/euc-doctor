from __future__ import annotations

from .common import AppSupportModule

MODULE = AppSupportModule(
    slug="anyconnect",
    display_name="Cisco Secure Client",
    bundle_patterns=(
        "/Applications/Cisco/Cisco Secure Client.app",
        "/Applications/Cisco/Cisco AnyConnect Secure Mobility Client.app",
    ),
    process_names=("Cisco Secure Client", "AnyConnect", "vpn", "acumbrellaagent"),
    cache_patterns=(
        "/opt/cisco/anyconnect",
        "/opt/cisco/secureclient",
    ),
    data_patterns=(
        "/opt/cisco/anyconnect",
        "/opt/cisco/secureclient",
    ),
    log_patterns=(
        "/opt/cisco/anyconnect/log",
        "/opt/cisco/secureclient/logs",
    ),
    support_summary="Cisco Secure Client, including AnyConnect-style VPN workflows, is a common support app because connectivity, posture, certificates, and split-tunnel expectations frequently break user workflows.",
    support_steps=(
        "Check whether the issue is app launch, sign-in, tunnel establishment, posture, or post-connect traffic.",
        "Cisco documents using the DART diagnostics bundle to gather logs and status before reinstalling the client.",
        "If the tunnel connects but apps still fail, compare DNS, routes, and captive portal or proxy behavior outside the VPN client.",
        "For certificate or posture prompts, keep the troubleshooting evidence because those flows are often organization-specific.",
    ),
    sources=(
        "Cisco Secure Client Admin Guide: https://www.cisco.com/c/en/us/td/docs/security/vpn_client/anyconnect/Cisco-Secure-Client-5/admin/guide/b-cisco-secure-client-admin-guide-5-1.pdf",
        "Cisco Troubleshoot AnyConnect: https://www.cisco.com/c/en/us/td/docs/security/vpn_client/anyconnect/anyconnect49/administration/guide/b_AnyConnect_Administrator_Guide_4-9/troubleshoot-anyconnect.pdf",
    ),
)
