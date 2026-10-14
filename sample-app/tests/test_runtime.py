import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx


def test_running_server_health_write_and_validation() -> None:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as logs:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--workers",
                "1",
            ],
            cwd=Path(__file__).resolve().parents[1],
            stdout=logs,
            stderr=subprocess.STDOUT,
        )
        try:
            with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=2) as client:
                deadline = time.monotonic() + 15
                while time.monotonic() < deadline and process.poll() is None:
                    try:
                        response = client.get("/health")
                    except httpx.ConnectError:
                        time.sleep(0.1)
                        continue
                    response.raise_for_status()
                    break
                else:
                    logs.seek(0)
                    raise AssertionError(f"Server did not become ready:\n{logs.read()}")
                assert response.json() == {"status": "ok"}
                assert len(client.get("/items").json()) == 2
                created = client.post("/items", json={"name": "runtime-item"})
                assert created.status_code == 201
                assert created.json() == {"id": 3, "name": "runtime-item"}
                assert client.get("/items").json()[-1] == created.json()
                assert client.post("/items", json={"name": ""}).status_code == 422
                assert len(client.get("/items").json()) == 3
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
