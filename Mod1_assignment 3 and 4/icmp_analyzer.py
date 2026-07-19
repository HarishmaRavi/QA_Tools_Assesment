import sys
import time
import argparse
from scapy.all import IP, ICMP, sr1


def analyze(target: str, count: int = 5, timeout: int = 2):
    print(f"Pinging {target} with {count} ICMP Echo Requests...\n")

    sent = 0
    received = 0
    rtts = []  # round-trip times in milliseconds

    for seq in range(1, count + 1):
        packet = IP(dst=target) / ICMP(seq=seq)
        sent += 1
        start_time = time.time()

        reply = sr1(packet, timeout=timeout, verbose=0)

        if reply is not None:
            rtt_ms = (time.time() - start_time) * 1000
            rtts.append(rtt_ms)
            received += 1
            print(f"Reply from {target}: seq={seq} time={rtt_ms:.2f} ms")
        else:
            print(f"Request timeout for seq={seq} (no reply)")

        time.sleep(1)  # small delay between pings, like normal 'ping'

    loss_percentage = ((sent - received) / sent) * 100 if sent else 0
    avg_rtt = sum(rtts) / len(rtts) if rtts else 0

    print("\n" + "=" * 50)
    print("PING STATISTICS")
    print("=" * 50)
    print(f"Target:              {target}")
    print(f"Packets sent:        {sent}")
    print(f"Packets received:    {received}")
    print(f"Packet loss:         {loss_percentage:.1f}%")
    print(f"Average RTT:         {avg_rtt:.2f} ms")
    print("=" * 50)

    return {
        "target": target,
        "sent": sent,
        "received": received,
        "loss_percentage": loss_percentage,
        "average_rtt_ms": avg_rtt,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ICMP packet analyzer using Scapy")
    parser.add_argument("target", nargs="?", default="8.8.8.8",
                         help="Target IP/hostname to ping (default: 8.8.8.8)")
    parser.add_argument("--count", type=int, default=5,
                         help="Number of ICMP requests to send (default: 5)")
    args = parser.parse_args()

    analyze(args.target, count=args.count)
