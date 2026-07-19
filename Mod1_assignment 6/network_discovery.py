"""
Assignment 6 - Network Discovery Tool

"""

import sys
import csv
import ipaddress
from collections import defaultdict
from scapy.all import ARP, Ether, srp, conf


def detect_local_subnet():
    """
    Auto-detects the local subnet by asking Scapy which interface/IP
    would be used to reach the internet, then assumes a /24 network.
    """
    iface, my_ip, gateway = conf.route.route("0.0.0.0")
    network = ipaddress.ip_network(f"{my_ip}/24", strict=False)
    return str(network)


def arp_scan(subnet: str, timeout: int = 3):
    """
    Sends an ARP 'who-has' broadcast for every IP in the subnet and
    collects every reply. Returns a list of (ip, mac) tuples - including
    duplicates, so we can later detect conflicting responses.
    """
    print(f"Scanning subnet: {subnet}\n")

    arp_request = ARP(pdst=subnet)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / arp_request

    answered, _unanswered = srp(packet, timeout=timeout, verbose=0)

    results = []
    for _sent, received in answered:
        results.append((received.psrc, received.hwsrc))

    return results


def find_duplicates(results):
    """
    Groups replies by IP address. If more than one distinct MAC address
    responded for the same IP, that IP is flagged as a duplicate/conflict.
    """
    ip_to_macs = defaultdict(set)
    for ip, mac in results:
        ip_to_macs[ip].add(mac)

    duplicates = {ip: macs for ip, macs in ip_to_macs.items() if len(macs) > 1}
    return ip_to_macs, duplicates


def save_to_csv(ip_to_macs, duplicates, filename="discovered_devices.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ip_address", "mac_address", "duplicate_ip"])
        for ip, macs in sorted(ip_to_macs.items(), key=lambda x: ipaddress.ip_address(x[0])):
            is_duplicate = "YES" if ip in duplicates else "NO"
            for mac in macs:
                writer.writerow([ip, mac, is_duplicate])
    print(f"\nResults saved to {filename}")


def main():
    subnet = sys.argv[1] if len(sys.argv) > 1 else detect_local_subnet()

    results = arp_scan(subnet)

    if not results:
        print("No devices responded. On a mobile hotspot this can happen "
              "if client isolation is enabled, or if no other devices are "
              "connected right now.")
        return

    ip_to_macs, duplicates = find_duplicates(results)

    print(f"{'IP Address':<18}{'MAC Address':<20}{'Duplicate?'}")
    print("-" * 50)
    for ip, macs in sorted(ip_to_macs.items(), key=lambda x: ipaddress.ip_address(x[0])):
        flag = "YES" if ip in duplicates else "NO"
        for mac in macs:
            print(f"{ip:<18}{mac:<20}{flag}")

    if duplicates:
        print(f"\n[ALERT] {len(duplicates)} duplicate IP(s) detected - "
              f"possible IP conflict or ARP spoofing:")
        for ip, macs in duplicates.items():
            print(f"  {ip} -> {', '.join(macs)}")
    else:
        print("\nNo duplicate IPs detected.")

    save_to_csv(ip_to_macs, duplicates)


if __name__ == "__main__":
    main()
