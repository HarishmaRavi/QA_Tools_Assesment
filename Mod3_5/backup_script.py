import os
import csv
import datetime
from pyats.topology import loader

def main():
    testbed = loader.load("testbed.yaml")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_folder = f"backup_{timestamp}"
    os.makedirs(backup_folder, exist_ok=True)

    report_rows = []

    for device_name, device in testbed.devices.items():
        platform = device.platform
        status = "Success"
        backup_filename = f"{device_name}_config.txt"
        backup_path = os.path.join(backup_folder, backup_filename)

        try:
            device.connect(log_stdout=False)
            config = device.execute("show running-config")
            device.disconnect()
        except Exception as e:
            # No real device available -> simulate output so script still works
            config = f"! Simulated config for {device_name} ({platform})\n! Connection error: {e}"
            status = "Simulated (no real device)"

        with open(backup_path, "w") as f:
            f.write(config)

        report_rows.append({
            "Device Name": device_name,
            "Platform": platform,
            "Status": status,
            "Backup File Name": backup_filename,
            "Date": timestamp
        })

    csv_path = os.path.join(backup_folder, "backup_report.csv")
    with open(csv_path, "w", newline="") as csvfile:
        fieldnames = ["Device Name", "Platform", "Status", "Backup File Name", "Date"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report_rows)

    print(f"Backup complete. Folder: {backup_folder}")
    print(f"CSV report: {csv_path}")

if __name__ == "__main__":
    main()