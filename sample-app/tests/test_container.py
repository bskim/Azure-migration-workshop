import os
import subprocess
import time
from uuid import uuid4

import httpx
import pytest


@pytest.mark.skipif(
    not os.environ.get("WORKSHOP_CONTAINER_IMAGE"),
    reason="Set WORKSHOP_CONTAINER_IMAGE to a locally built workshop image.",
)
def test_container_health_write_and_read_back() -> None:
    image = os.environ["WORKSHOP_CONTAINER_IMAGE"]
    container_id = subprocess.check_output(
        [
            "docker",
            "run",
            "--detach",
            "--name",
            f"amw-test-{uuid4().hex[:8]}",
            "--publish",
            "127.0.0.1::8080",
            "--memory",
            "256m",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            image,
        ],
        text=True,
    ).strip()
    try:
        address = subprocess.check_output(
            ["docker", "port", container_id, "8080/tcp"], text=True
        ).strip()
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            state = subprocess.check_output(
                [
                    "docker",
                    "inspect",
                    "--format",
                    "{{.State.Running}} {{.State.Health.Status}}",
                    container_id,
                ],
                text=True,
            ).strip()
            if state == "true healthy":
                break
            if not state.startswith("true ") or state == "true unhealthy":
                logs = subprocess.check_output(
                    ["docker", "logs", container_id], stderr=subprocess.STDOUT, text=True
                )
                raise AssertionError(f"Container state is {state}:\n{logs}")
            time.sleep(0.5)
        else:
            logs = subprocess.check_output(
                ["docker", "logs", container_id], stderr=subprocess.STDOUT, text=True
            )
            raise AssertionError(f"Container did not become healthy:\n{logs}")
        with httpx.Client(base_url=f"http://{address}", timeout=2) as client:
            response = client.get("/health")
            response.raise_for_status()
            assert response.json() == {"status": "ok"}
            assert len(client.get("/items").json()) == 2
            created = client.post("/items", json={"name": "container-item"})
            assert created.status_code == 201
            assert created.json() == {"id": 3, "name": "container-item"}
            assert client.get("/items").json()[-1] == created.json()
            assert client.post("/items", json={"name": ""}).status_code == 422
            assert len(client.get("/items").json()) == 3
        user = subprocess.check_output(
            ["docker", "inspect", "--format", "{{.Config.User}}", container_id], text=True
        ).strip()
        assert user == "10001:10001"
    finally:
        subprocess.run(["docker", "rm", "--force", container_id], check=True)
