"""
fake_device_server.py

Simulates Cisco-like network devices over real SSH, using Paramiko's
server-side API. This lets you test Assignment 1 (health_collector.py)
without any real hardware or a network simulator like GNS3.

Run this FIRST, in its own terminal, and leave it running:
    python3 fake_device_server.py

It starts 3 fake devices on localhost:
    127.0.0.1:2201  -> "Router1" (user: admin / pass: cisco123)   -> works
    127.0.0.1:2202  -> "Router2" (user: admin / pass: cisco123)   -> works
    127.0.0.1:2203  -> "Router3" (user: admin / pass: wrongpass)  -> auth will
                       fail on purpose, so you can see failure handling
                       and retry logic in health_collector.py
"""

import socket
import threading
import paramiko
import os

HOST_KEY_PATH = "fake_host_key.rsa"

CANNED_OUTPUT = {
    "show version": (
        "Cisco IOS Software, Version 15.2(4)M6\n"
        "ROM: System Bootstrap, Version 15.2\n"
        "Uptime is 3 weeks, 2 days, 4 hours, 10 minutes\n"
        "System image file is \"flash:c2900-universalk9-mz.SPA.bin\"\n"
        "cisco 2911/K9 chassis, Processor board ID FTX1840AAV\n"
    ),
    "show ip interface brief": (
        "Interface                  IP-Address      OK? Method Status                Protocol\n"
        "GigabitEthernet0/0          192.168.1.1     YES manual up                    up\n"
        "GigabitEthernet0/1          unassigned      YES unset  administratively down down\n"
        "GigabitEthernet0/2          10.10.10.1      YES manual up                    up\n"
        "Loopback0                   1.1.1.1         YES manual up                    up\n"
    ),
}


def get_host_key():
    if not os.path.exists(HOST_KEY_PATH):
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(HOST_KEY_PATH)
    return paramiko.RSAKey(filename=HOST_KEY_PATH)


class FakeDeviceServer(paramiko.ServerInterface):
    def __init__(self, valid_username, valid_password):
        self.event = threading.Event()
        self.valid_username = valid_username
        self.valid_password = valid_password

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if username == self.valid_username and password == self.valid_password:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True


def handle_client(client_sock, hostname, valid_username, valid_password):
    try:
        transport = paramiko.Transport(client_sock)
        transport.add_server_key(get_host_key())
        server = FakeDeviceServer(valid_username, valid_password)
        transport.start_server(server=server)

        channel = transport.accept(20)
        if channel is None:
            return

        server.event.wait(10)
        prompt = f"{hostname}#"
        channel.send(f"\r\n{prompt} ")

        buffer = ""
        while True:
            data = channel.recv(1024)
            if not data:
                break
            text = data.decode(errors="ignore")
            channel.send(text)  # local echo

            buffer += text
            if "\n" in buffer or "\r" in buffer:
                command = buffer.strip().lower()
                buffer = ""

                if command in ("exit", "quit"):
                    channel.send("\r\n")
                    break
                elif command in CANNED_OUTPUT:
                    output = CANNED_OUTPUT[command]
                    channel.send("\r\n" + output.replace("\n", "\r\n"))
                elif command == "":
                    pass
                else:
                    channel.send(f"\r\n% Invalid input detected: {command}\r\n")

                channel.send(f"\r\n{prompt} ")

        channel.close()
    except Exception as e:
        print(f"[{hostname}] connection error: {e}")
    finally:
        try:
            transport.close()
        except Exception:
            pass


def start_device(port, hostname, valid_username, valid_password):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", port))
    sock.listen(5)
    print(f"[{hostname}] listening on 127.0.0.1:{port} "
          f"(user={valid_username}, pass={valid_password})")

    while True:
        client_sock, addr = sock.accept()
        threading.Thread(
            target=handle_client,
            args=(client_sock, hostname, valid_username, valid_password),
            daemon=True,
        ).start()


if __name__ == "__main__":
    devices = [
        (2201, "Router1", "admin", "cisco123"),
        (2202, "Router2", "admin", "cisco123"),
        (2203, "Router3", "admin", "cisco123"),  # health_collector.py will use a
                                                   # WRONG password for this one
                                                   # to demonstrate a failed connection
    ]

    threads = []
    for port, hostname, user, pw in devices:
        t = threading.Thread(target=start_device, args=(port, hostname, user, pw), daemon=True)
        t.start()
        threads.append(t)

    print("\nFake devices are up. Leave this running and open a NEW terminal")
    print("to run health_collector.py.\n")

    for t in threads:
        t.join()
