"""
Assignment 2 - CLI Output Parser
Parses 'show ip interface brief' output into a nested Python dictionary
WITHOUT using TextFSM or Genie parsers - pure string/regex parsing.
"""

import re


def parse_show_ip_interface_brief(raw_output: str) -> dict:
    """
    Parses Cisco IOS 'show ip interface brief' output.

    Typical line format:
    Interface       IP-Address      OK? Method Status                Protocol
    GigabitEthernet0/0  192.168.1.1   YES manual up                    up

    Returns a nested dict:
    {
        "GigabitEthernet0/0": {
            "ip_address": "192.168.1.1",
            "ok": "YES",
            "method": "manual",
            "status": "up",
            "protocol": "up"
        },
        ...
    }
    """
    parsed = {}
    lines = raw_output.strip().splitlines()

    for line in lines:
        line = line.strip()

        # Skip empty lines and the header line
        if not line or line.lower().startswith("interface"):
            continue

        # Split on whitespace, but status can be two words e.g. "administratively down"
        # so we use a regex that captures the last two fields (status, protocol)
        # and the middle fields (ok, method) separately.
        match = re.match(
            r"^(?P<interface>\S+)\s+"
            r"(?P<ip_address>\S+)\s+"
            r"(?P<ok>\S+)\s+"
            r"(?P<method>\S+)\s+"
            r"(?P<status>administratively down|up|down)\s+"
            r"(?P<protocol>up|down)\s*$",
            line,
        )

        if match:
            data = match.groupdict()
            interface = data.pop("interface")
            parsed[interface] = data
        else:
            # Keep track of any line that didn't match, useful for debugging
            parsed.setdefault("_unparsed_lines", []).append(line)

    return parsed


if __name__ == "__main__":
    sample_input = """Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0          192.168.1.1     YES manual up                    up
GigabitEthernet0/1          unassigned      YES unset  administratively down down
GigabitEthernet0/2          10.10.10.1      YES manual up                    up
Loopback0                   1.1.1.1         YES manual up                    up
Vlan1                       unassigned      YES unset  down                  down
"""

    print("=== SAMPLE INPUT ===")
    print(sample_input)

    result = parse_show_ip_interface_brief(sample_input)

    print("=== PARSED OUTPUT ===")
    import json
    print(json.dumps(result, indent=4))
