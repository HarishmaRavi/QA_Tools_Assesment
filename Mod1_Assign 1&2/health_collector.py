"""
Assignment 1 - Network Device Health Collector

- Reads devices from devices.csv
- Connects to each device over SSH using Paramiko
- Runs 'show version' and 'show ip interface brief'
- Saves output to logs/<hostname>.log
- Prints/saves a summary report: success, failed, execution time, failure reason
- Bonus: retries failed connections up to MAX_RETRIES times
"""

import csv
import os
import socket
import time
import paramiko

LOG_DIR = "logs"
COMMANDS = ["show version", "show ip interface brief"]
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2


def read_devices(csv_path):
    devices = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            devices.append(row)
    return devices


def read_until_prompt(channel, timeout=5):
    """Reads from the channel until no more data arrives for `timeout` seconds."""
    channel.settimeout(timeout)
    output = ""
    try:
        while True:
            chunk = channel.recv(4096).decode(errors="ignore")
            if not chunk:
                break
            output += chunk
    except Exception:
        pass  # timeout reached, assume device finished sending output
    return output


def connect_and_collect(hostname, ip, port, username, password):
    """
    Connects to a single device, runs COMMANDS, and returns:
    (success: bool, log_text: str, failure_reason: str or None)
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=ip,
            port=int(port),
            username=username,
            password=password,
            timeout=8,
            look_for_keys=False,
            allow_agent=False,
        )

        channel = client.invoke_shell()
        time.sleep(1)
        read_until_prompt(channel, timeout=2)  # clear initial banner/prompt

        full_log = ""
        for cmd in COMMANDS:
            channel.send(cmd + "\n")
            time.sleep(1)
            output = read_until_prompt(channel, timeout=3)
            full_log += f"\n$ {cmd}\n{output}\n"

        client.close()
        return True, full_log, None

    except paramiko.AuthenticationException:
        return False, "", "Authentication failed (bad username/password)"
    except (paramiko.SSHException, socket.timeout, socket.error) as e:
        return False, "", f"SSH error: {e}"
    except Exception as e:
        return False, "", f"Unexpected error: {e}"


def main():
    os.makedirs(LOG_DIR, exist_ok=True)
    devices = read_devices("devices.csv")

    summary = []

    for device in devices:
        hostname = device["hostname"]
        ip = device["ip"]
        port = device["port"]
        username = device["username"]
        password = device["password"]

        attempt = 0
        success = False
        failure_reason = None
        log_text = ""
        start_time = time.time()

        while attempt < MAX_RETRIES and not success:
            attempt += 1
            print(f"[{hostname}] Attempt {attempt}/{MAX_RETRIES}...")
            success, log_text, failure_reason = connect_and_collect(
                hostname, ip, port, username, password
            )
            if not success and attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)

        elapsed = round(time.time() - start_time, 2)

        if success:
            log_path = os.path.join(LOG_DIR, f"{hostname}.log")
            with open(log_path, "w") as f:
                f.write(log_text)
            print(f"[{hostname}] SUCCESS - saved to {log_path}")
        else:
            print(f"[{hostname}] FAILED after {attempt} attempt(s): {failure_reason}")

        summary.append({
            "hostname": hostname,
            "status": "SUCCESS" if success else "FAILED",
            "attempts": attempt,
            "execution_time_sec": elapsed,
            "failure_reason": failure_reason or "-",
        })

    print_summary_report(summary)
    save_summary_report(summary)


def print_summary_report(summary):
    print("\n" + "=" * 70)
    print("SUMMARY REPORT")
    print("=" * 70)
    successful = [s for s in summary if s["status"] == "SUCCESS"]
    failed = [s for s in summary if s["status"] == "FAILED"]

    print(f"Successful connections: {len(successful)}")
    print(f"Failed connections:     {len(failed)}")
    print("-" * 70)
    for s in summary:
        print(f"{s['hostname']:<10} {s['status']:<8} "
              f"time={s['execution_time_sec']}s  attempts={s['attempts']}  "
              f"reason={s['failure_reason']}")
    print("=" * 70)


def save_summary_report(summary, path="logs/summary_report.txt"):
    with open(path, "w") as f:
        successful = [s for s in summary if s["status"] == "SUCCESS"]
        failed = [s for s in summary if s["status"] == "FAILED"]
        f.write("SUMMARY REPORT\n")
        f.write(f"Successful connections: {len(successful)}\n")
        f.write(f"Failed connections: {len(failed)}\n\n")
        for s in summary:
            f.write(f"{s['hostname']} | {s['status']} | "
                    f"time={s['execution_time_sec']}s | attempts={s['attempts']} | "
                    f"reason={s['failure_reason']}\n")


if __name__ == "__main__":
    main()
