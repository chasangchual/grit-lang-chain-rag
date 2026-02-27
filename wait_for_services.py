import subprocess
import sys
import time

SERVICES = [
    "grit-postgres",
    "grit-minio",
    "grit-neo4j",
    "grit-redis"
]

TIMEOUT_SECONDS = 120
POLL_INTERVAL = 3


def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def is_container_running(name):
    code, out, _ = run_cmd(f"docker inspect -f '{{{{.State.Running}}}}' {name}")
    return code == 0 and out == "true"


def get_health_status(name):
    code, out, _ = run_cmd(
        f"docker inspect -f '{{{{if .State.Health}}}}{{{{.State.Health.Status}}}}{{{{else}}}}no-healthcheck{{{{end}}}}' {name}"
    )
    if code != 0:
        return None
    return out


def wait_for_service(name):
    print(f"Waiting for {name}...")

    start = time.time()

    while time.time() - start < TIMEOUT_SECONDS:

        if not is_container_running(name):
            print(f"❌ {name} is not running")
            return False

        health = get_health_status(name)

        if health == "healthy" or health == "no-healthcheck":
            print(f"✅ {name} is ready ({health})")
            return True

        print(f"⏳ {name} status: {health}... retrying")
        time.sleep(POLL_INTERVAL)

    print(f"❌ Timeout waiting for {name}")
    return False


def main():
    all_ok = True

    for service in SERVICES:
        if not wait_for_service(service):
            all_ok = False

    if not all_ok:
        print("\nSome services failed.")
        sys.exit(1)

    print("\nAll services are up and healthy.")
    sys.exit(0)


if __name__ == "__main__":
    main()
