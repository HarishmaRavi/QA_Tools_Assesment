"""
Assignment 4 - Coding + Analysis: iPerf3 Automation

- Runs an iperf3 client test against a server (using JSON output for
  reliable parsing instead of scraping plain text).
- Parses average bandwidth, total retransmissions, and test duration.
- Prints all three.
- Fails the script (non-zero exit code) if bandwidth is below 800 Mbps.

Usage:
    python3 iperf_benchmark.py <server_ip> [--port 5201] [--duration 10]

Example (against your phone hotspot, like in Module 2 Assignment 1):
    python3 iperf_benchmark.py 192.168.242.89

Example (against a local iperf3 server, for a PASS scenario - localhost
throughput is normally in the multi-Gbps range, well above 800 Mbps):
    # Terminal 1:
    iperf3 -s
    # Terminal 2:
    python3 iperf_benchmark.py 127.0.0.1
"""

import subprocess
import json
import sys
import argparse

BANDWIDTH_THRESHOLD_MBPS = 800


def run_iperf_test(server: str, port: int = 5201, duration: int = 10) -> dict:
    """
    Runs 'iperf3 -c <server> -J' and returns the parsed JSON result.
    Raises RuntimeError if iperf3 isn't installed or the test fails to run.
    """
    command = ["iperf3", "-c", server, "-p", str(port), "-t", str(duration), "-J"]

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=duration + 15
        )
    except FileNotFoundError:
        raise RuntimeError(
            "iperf3 is not installed or not found in PATH. "
            "Install it with: sudo apt install iperf3"
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("iperf3 test timed out.")

    if result.returncode != 0:
        raise RuntimeError(f"iperf3 failed: {result.stderr.strip()}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"Could not parse iperf3 output as JSON:\n{result.stdout}")


def parse_results(data: dict) -> dict:
    """
    Pulls average bandwidth, retransmissions, and duration out of the
    iperf3 JSON structure.
    """
    end = data["end"]
    sent = end["sum_sent"]

    bandwidth_bps = sent["bits_per_second"]
    bandwidth_mbps = bandwidth_bps / 1_000_000

    # Retransmits only appears for TCP tests, not UDP
    retransmits = sent.get("retransmits", "N/A (not applicable for UDP)")

    duration_sec = sent["seconds"]

    return {
        "average_bandwidth_mbps": round(bandwidth_mbps, 2),
        "total_retransmissions": retransmits,
        "test_duration_sec": round(duration_sec, 2),
    }


def main():
    parser = argparse.ArgumentParser(description="iPerf3 automated benchmark with pass/fail threshold")
    parser.add_argument("server", help="iperf3 server IP address")
    parser.add_argument("--port", type=int, default=5201, help="iperf3 server port (default: 5201)")
    parser.add_argument("--duration", type=int, default=10, help="Test duration in seconds (default: 10)")
    args = parser.parse_args()

    print(f"Running iperf3 TCP test against {args.server}:{args.port} for {args.duration}s...\n")

    try:
        raw_data = run_iperf_test(args.server, args.port, args.duration)
    except RuntimeError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    results = parse_results(raw_data)

    print("=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    print(f"Average Bandwidth:     {results['average_bandwidth_mbps']} Mbps")
    print(f"Total Retransmissions: {results['total_retransmissions']}")
    print(f"Test Duration:         {results['test_duration_sec']} sec")
    print("=" * 50)

    if results["average_bandwidth_mbps"] < BANDWIDTH_THRESHOLD_MBPS:
        print(f"\nRESULT: FAIL - bandwidth ({results['average_bandwidth_mbps']} Mbps) "
              f"is below the {BANDWIDTH_THRESHOLD_MBPS} Mbps threshold.")
        sys.exit(1)
    else:
        print(f"\nRESULT: PASS - bandwidth ({results['average_bandwidth_mbps']} Mbps) "
              f"meets the {BANDWIDTH_THRESHOLD_MBPS} Mbps threshold.")
        sys.exit(0)


if __name__ == "__main__":
    main()
