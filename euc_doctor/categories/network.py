from __future__ import annotations

import socket
import ssl
from datetime import datetime, timezone

from euc_doctor.models import ActionCategory, ActionDefinition, ActionResult, ActionType, ExecutionContext, Severity
from euc_doctor.utils import info_result, is_macos, run_cmd, skip_non_macos


def _network_summary(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    route = run_cmd(["route", "-n", "get", "default"])
    dns = run_cmd(["scutil", "--dns"])
    detail_parts = []
    if route.stdout:
        detail_parts.append(route.stdout[:900])
    if dns.stdout:
        detail_parts.append(dns.stdout[:900])
    return ActionResult(
        action.action_id,
        action.category,
        action.action_type,
        action.name,
        Severity.OK if route.ok else Severity.WARN,
        "Collected default route and DNS configuration.",
        "\n\n".join(detail_parts) or route.stderr or dns.stderr or None,
    )


def _dns_resolution(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    hosts = ["github.com", "apple.com", "google.com"]
    rows = []
    failures = 0
    for host in hosts:
        try:
            rows.append(f"{host}: {socket.gethostbyname(host)}")
        except OSError as exc:
            failures += 1
            rows.append(f"{host}: failed ({exc})")
    severity = Severity.FAIL if failures == len(hosts) else Severity.WARN if failures else Severity.OK
    return ActionResult(action.action_id, action.category, action.action_type, action.name, severity, "Resolved common endpoints.", "\n".join(rows))


def _proxy(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["scutil", "--proxy"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected system proxy settings.", result.stdout or result.stderr or None)


def _dns_servers(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["scutil", "--dns"])
    lines = [line.strip() for line in result.stdout.splitlines() if "nameserver" in line.lower()]
    detail = "\n".join(lines[:12]) if lines else result.stdout[:1200] or result.stderr or None
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected configured DNS servers.", detail)


def _latency(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["ping", "-c", "2", "8.8.8.8"], timeout=10)
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.OK if result.ok else Severity.WARN, "Ran a basic ping test to 8.8.8.8.", result.stdout or result.stderr or None)


def _interfaces(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    hardware = run_cmd(["networksetup", "-listallhardwareports"])
    interfaces = run_cmd(["ifconfig"])
    detail = "\n\n".join(part for part in [hardware.stdout[:1200], interfaces.stdout[:1200]] if part)
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if hardware.ok or interfaces.ok else Severity.WARN, "Collected interface and hardware port data.", detail or hardware.stderr or interfaces.stderr or None)


def _wifi(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    airport = run_cmd(["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"])
    if airport.ok and airport.stdout:
        return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO, "Collected current Wi-Fi details.", airport.stdout)
    fallback = run_cmd(["system_profiler", "SPAirPortDataType"], timeout=20)
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if fallback.ok else Severity.WARN, "Collected Wi-Fi information.", fallback.stdout[:1400] or fallback.stderr or None)


def _ports(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"], timeout=20)
    lines = result.stdout.splitlines() if result.stdout else []
    detail = "\n".join(lines[:20]) if lines else result.stderr or "No listening TCP ports were returned."
    severity = Severity.WARN if len(lines) > 1 else Severity.INFO if result.ok else Severity.WARN
    return ActionResult(action.action_id, action.category, action.action_type, action.name, severity, "Collected locally listening TCP ports.", detail)


def _vpn(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["scutil", "--nc", "list"])
    return ActionResult(action.action_id, action.category, action.action_type, action.name, Severity.INFO if result.ok else Severity.WARN, "Collected configured network connection services, including VPN entries.", result.stdout or result.stderr or None)


def _cert_check(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    endpoints = ["github.com", "apple.com"]
    rows = []
    failures = 0
    for host in endpoints:
        try:
            with socket.create_connection((host, 443), timeout=5) as sock:
                with ssl.create_default_context().wrap_socket(sock, server_hostname=host) as secure_sock:
                    cert = secure_sock.getpeercert()
            subject = ", ".join(f"{key}={value}" for item in cert.get("subject", []) for key, value in item)
            issuer = ", ".join(f"{key}={value}" for item in cert.get("issuer", []) for key, value in item)
            expires = cert.get("notAfter", "unknown")
            rows.append(f"{host}: subject [{subject}] | issuer [{issuer}] | expires {expires}")
        except OSError as exc:
            failures += 1
            rows.append(f"{host}: failed ({exc})")
    severity = Severity.FAIL if failures == len(endpoints) else Severity.WARN if failures else Severity.OK
    return ActionResult(action.action_id, action.category, action.action_type, action.name, severity, "Checked TLS certificate handshakes for common endpoints.", "\n".join(rows))


def _captive_portal(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    if not is_macos():
        return skip_non_macos(action)
    result = run_cmd(["curl", "-sL", "--max-time", "10", "http://captive.apple.com/hotspot-detect.html"], timeout=15)
    body = result.stdout.strip()
    severity = Severity.OK if body == "Success" else Severity.WARN
    message = "No captive portal behavior detected." if body == "Success" else "Response differed from the expected captive portal test page."
    return ActionResult(action.action_id, action.category, action.action_type, action.name, severity, message, body or result.stderr or None)


def _renew_dhcp(_: ExecutionContext, action: ActionDefinition) -> ActionResult:
    return info_result(action, "Manual-only for now.", "Suggested command: sudo ipconfig set en0 DHCP\nThis remains INFO first because the active interface varies across Macs and docks.")


ACTIONS = [
    ActionDefinition("net.summary", ActionCategory.NETWORK, ActionType.DIAGNOSE, "Network summary", "Collect default route and current DNS configuration.", _network_summary),
    ActionDefinition("net.dns", ActionCategory.NETWORK, ActionType.DIAGNOSE, "DNS resolution test", "Resolve a short list of common domains to catch obvious resolver issues.", _dns_resolution),
    ActionDefinition("net.proxy", ActionCategory.NETWORK, ActionType.DIAGNOSE, "Proxy settings", "Show configured macOS proxy settings for the current machine.", _proxy),
    ActionDefinition("net.dns_servers", ActionCategory.NETWORK, ActionType.DIAGNOSE, "DNS servers", "List configured DNS servers from macOS resolver configuration.", _dns_servers),
    ActionDefinition("net.latency", ActionCategory.NETWORK, ActionType.DIAGNOSE, "Basic latency check", "Run a short ping test to a public IP address.", _latency),
    ActionDefinition("net.interfaces", ActionCategory.NETWORK, ActionType.DIAGNOSE, "Network interfaces", "Show hardware ports and current interface configuration.", _interfaces),
    ActionDefinition("net.wifi", ActionCategory.NETWORK, ActionType.DIAGNOSE, "Wi-Fi details", "Show current Wi-Fi connection details when available.", _wifi),
    ActionDefinition("net.ports", ActionCategory.NETWORK, ActionType.DIAGNOSE, "Listening ports", "List local listening TCP ports to catch conflicts.", _ports),
    ActionDefinition("net.vpn", ActionCategory.NETWORK, ActionType.DIAGNOSE, "VPN services", "List configured and active network connection services, including VPN entries.", _vpn),
    ActionDefinition("net.cert_check", ActionCategory.NETWORK, ActionType.DIAGNOSE, "TLS certificate check", "Perform TLS handshakes to common endpoints and summarize certificate details.", _cert_check),
    ActionDefinition("net.captive_portal", ActionCategory.NETWORK, ActionType.DIAGNOSE, "Captive portal check", "Detect whether a captive portal may be intercepting plain HTTP traffic.", _captive_portal),
    ActionDefinition("net.renew_dhcp", ActionCategory.NETWORK, ActionType.INFO, "Renew DHCP lease", "Explain the safest manual DHCP renewal path before automation is added.", _renew_dhcp, touches=("en0",), requires_admin=True),
]
