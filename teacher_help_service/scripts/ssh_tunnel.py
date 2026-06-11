import os
import signal
import sys
import time

from sshtunnel import SSHTunnelForwarder


def get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value else default


def main() -> int:
    ssh_host = os.getenv("SSH_TUNNEL_HOST", "159.75.155.106")
    ssh_user = os.getenv("SSH_TUNNEL_USER", "ubuntu")
    ssh_password = os.getenv("SSH_TUNNEL_PASSWORD")
    local_db_port = get_int_env("SSH_TUNNEL_LOCAL_DB_PORT", 13306)
    local_redis_port = get_int_env("SSH_TUNNEL_LOCAL_REDIS_PORT", 16379)

    if not ssh_password:
        print("SSH_TUNNEL_PASSWORD is required", file=sys.stderr)
        return 2

    server = SSHTunnelForwarder(
        (ssh_host, 22),
        ssh_username=ssh_user,
        ssh_password=ssh_password,
        local_bind_addresses=[
            ("127.0.0.1", local_db_port),
            ("127.0.0.1", local_redis_port),
        ],
        remote_bind_addresses=[
            ("127.0.0.1", 3306),
            ("127.0.0.1", 6379),
        ],
    )

    stop = False

    def request_stop(signum, frame):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)

    server.start()
    print(
        f"SSH tunnel active: 127.0.0.1:{local_db_port}->127.0.0.1:3306, "
        f"127.0.0.1:{local_redis_port}->127.0.0.1:6379",
        flush=True,
    )

    try:
        while not stop:
            time.sleep(1)
    finally:
        server.stop()
        print("SSH tunnel stopped", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
