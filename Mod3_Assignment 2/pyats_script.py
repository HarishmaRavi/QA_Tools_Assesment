

import re
import csv
from datetime import datetime
from pyats.topology import loader

TESTBED_FILE = "testbed.yaml"
CSV_REPORT = "pyats_report.csv"
HTML_REPORT = "pyats_report.html"

VERSION_RE = re.compile(r"Version\s+([\d\.\(\)A-Za-z]+)")
IMAGE_RE = re.compile(r'System image file is\s+"([^"]+)"')


def parse_version(output: str) -> dict:
    version_match = VERSION_RE.search(output)
    image_match = IMAGE_RE.search(output)
    return {
        "ios_version": version_match.group(1) if version_match else "N/A",
        "image_file": image_match.group(1) if image_match else "N/A",
    }


def run_against_testbed():
    testbed = loader.load(TESTBED_FILE)
    results = []

    for name, device in testbed.devices.items():
        print(f"\nConnecting to {name}...")
        row = {
            "hostname": name, "status": "", "ios_version": "",
            "image_file": "", "inventory_summary": "", "error": "",
        }
        try:
            device.connect(log_stdout=False, learn_hostname=True, timeout=15)

            version_output = device.execute("show version")
            inventory_output = device.execute("show inventory")

            parsed = parse_version(version_output)
            row["ios_version"] = parsed["ios_version"]
            row["image_file"] = parsed["image_file"]
            row["inventory_summary"] = (
                inventory_output.strip().splitlines()[0]
                if inventory_output.strip() else "N/A"
            )
            row["status"] = "SUCCESS"

            device.disconnect()
            print(f"[{name}] SUCCESS")

        except Exception as e:
            row["status"] = "FAILED"
            row["error"] = str(e)
            print(f"[{name}] FAILED: {e}")

        results.append(row)

    return results


def save_csv(results, filename=CSV_REPORT):
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["hostname", "status", "ios_version",
                           "image_file", "inventory_summary", "error"]
        )
        writer.writeheader()
        writer.writerows(results)
    print(f"\nCSV report saved to {filename}")


def save_html(results, filename=HTML_REPORT):
    rows_html = ""
    for r in results:
        color = "#d4f7d4" if r["status"] == "SUCCESS" else "#f7d4d4"
        rows_html += f"""
        <tr style="background-color:{color}">
            <td>{r['hostname']}</td>
            <td>{r['status']}</td>
            <td>{r['ios_version']}</td>
            <td>{r['image_file']}</td>
            <td>{r['inventory_summary']}</td>
            <td>{r['error']}</td>
        </tr>"""

    html = f"""<html>
<head><title>pyATS Automation Report</title></head>
<body>
<h2>pyATS Automation Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h2>
<table border="1" cellpadding="6" cellspacing="0">
<tr><th>Hostname</th><th>Status</th><th>IOS Version</th><th>Image File</th><th>Inventory</th><th>Error</th></tr>
{rows_html}
</table>
</body>
</html>"""

    with open(filename, "w") as f:
        f.write(html)
    print(f"HTML report saved to {filename}")


if __name__ == "__main__":
    results = run_against_testbed()
    save_csv(results)
    save_html(results)
