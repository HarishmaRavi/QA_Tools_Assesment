"""
Assignment 4 - Configuration Compliance Checker

Connects to each device, pulls its running-config and logs, and checks:
  1. Is Telnet still enabled on the VTY lines? (should be SSH only)
  2. Is the default/well-known SNMP community string ("public"/"private") active?
  3. Is the HTTP server enabled? (should be disabled - "no ip http server")
  4. Are there any failed-login / unauthorized-access attempts in the logs?
     (detected using regex against %SEC_LOGIN-4-LOGIN_FAILED style messages)

Saves a per-device compliance report to logs/<hostname>_compliance.log
"""

import csv
import os
import re
import socket
import time
import paramiko

LOG_DIR = "logs"

# Regex patterns for compliance checks
TELNET_ENABLED_RE = re.compile(r"transport input.*\btelnet\b", re.IGNORECASE)
SNMP_DEFAULT_COMMUNITY_RE = re.compile(
    r"snmp-server community\s+(public|private)\b", re.IGNORECASE
)
HTTP_SERVER_ENABLED_RE = re.compile(
    r"^(?!no\s)ip http server\b", re.IGNORECASE | re.MULTILINE
)
FAILED_LOGIN_RE = re.compile(
    r"%SEC_LOGIN-4-LOGIN_FAILED:.*\[user:\s*(?P<user>\S+)\].*"
    r"\[Source:\s*(?P<source>\S+)\].*\[Reason:\s*(?P<reason>[^\]]+)\]",
    re.IGNORECASE,
)


def read_devices(csv_path):
    with open(csv_path, newline="") as f:
        return list(csv.DictReader(f))


def read_until_prompt(channel, timeout=5):
    channel.settimeout(timeout)
    output = ""
    try:
        while True:
            chunk = channel.recv(4096).decode(errors="ignore")
            if not chunk:
                break
            output += chunk
    except Exception:
        pass
    return output


def run_command(channel, command, wait=2):
    channel.send(command + "\n")
    time.sleep(wait)
    return read_until_prompt(channel, timeout=3)


def check_compliance(hostname, ip, port, username, password):
    """
    Connects to one device and runs the compliance checks.
    Returns (connected: bool, report_text: str, error: str or None)
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=ip, port=int(port), username=username, password=password,
            timeout=8, look_for_keys=False, allow_agent=False,
        )
        channel = client.invoke_shell()
        time.sleep(1)
        read_until_prompt(channel, timeout=2)

        running_config = run_command(channel, "show running-config")
        logging_output = run_command(channel, "show logging")
        client.close()

        report_lines = []
        report_lines.append(f"COMPLIANCE REPORT - {hostname}")
        report_lines.append("=" * 60)

        # Check 1: Telnet
        if TELNET_ENABLED_RE.search(running_config):
            report_lines.append("[FAIL] Telnet is enabled on VTY lines "
                                 "(should be SSH only)")
        else:
            report_lines.append("[PASS] Telnet is disabled - SSH only")

        # Check 2: Default SNMP community strings
        snmp_matches = SNMP_DEFAULT_COMMUNITY_RE.findall(running_config)
        if snmp_matches:
            found = ", ".join(sorted(set(snmp_matches)))
            report_lines.append(f"[FAIL] Default SNMP community string(s) found: {found}")
        else:
            report_lines.append("[PASS] No default SNMP community strings found")

        # Check 3: HTTP server
        if HTTP_SERVER_ENABLED_RE.search(running_config):
            report_lines.append("[FAIL] HTTP server is enabled (should be disabled)")
        else:
            report_lines.append("[PASS] HTTP server is disabled")

        # Check 4: Failed login / unauthorized access attempts
        failed_logins = FAILED_LOGIN_RE.finditer(logging_output)
        failed_count = 0
        for match in failed_logins:
            failed_count += 1
            report_lines.append(
                f"[ALERT] Failed login attempt - user: {match.group('user')}, "
                f"source: {match.group('source')}, reason: {match.group('reason')}"
            )
        if failed_count == 0:
            report_lines.append("[PASS] No failed login attempts found in logs")
        else:
            report_lines.append(f"[FAIL] {failed_count} failed login attempt(s) detected")

        report_lines.append("=" * 60)
        report_lines.append("\n--- RAW: show running-config ---\n" + running_config)
        report_lines.append("\n--- RAW: show logging ---\n" + logging_output)

        return True, "\n".join(report_lines), None

    except paramiko.AuthenticationException:
        return False, "", "Authentication failed (bad username/password)"
    except (paramiko.SSHException, socket.timeout, socket.error) as e:
        return False, "", f"SSH error: {e}"
    except Exception as e:
        return False, "", f"Unexpected error: {e}"


def main():
    os.makedirs(LOG_DIR, exist_ok=True)
    devices = read_devices("devices.csv")

    for device in devices:
        hostname = device["hostname"]
        print(f"\nChecking {hostname}...")

        connected, report, error = check_compliance(
            hostname, device["ip"], device["port"],
            device["username"], device["password"],
        )

        if connected:
            log_path = os.path.join(LOG_DIR, f"{hostname}_compliance.log")
            with open(log_path, "w") as f:
                f.write(report)
            print(f"[{hostname}] Compliance check complete - saved to {log_path}")
            for line in report.splitlines():
                if line.startswith(("[PASS]", "[FAIL]", "[ALERT]")):
                    print("  " + line)
        else:
            print(f"[{hostname}] SKIPPED - could not connect: {error}")


if __name__ == "__main__":
    main()
