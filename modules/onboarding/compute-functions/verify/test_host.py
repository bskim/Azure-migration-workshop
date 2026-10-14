import os
import time
from urllib.parse import urlsplit

import httpx
import pytest


@pytest.mark.skipif(
    not os.environ.get("WORKSHOP_FUNCTIONS_LOCAL_URL"),
    reason="Set WORKSHOP_FUNCTIONS_LOCAL_URL for a fresh isolated local host.",
)
def test_local_host_health_write_read_and_invalid_input():
    endpoint = os.environ["WORKSHOP_FUNCTIONS_LOCAL_URL"]
    parsed = urlsplit(endpoint)
    if (
        parsed.scheme != "http"
        or parsed.hostname != "127.0.0.1"
        or parsed.username
        or parsed.password
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Use an isolated HTTP host on 127.0.0.1, without credentials.")
    with httpx.Client(base_url=endpoint, timeout=5, trust_env=False) as client:
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            try:
                health = client.get("/health")
            except httpx.ConnectError:
                time.sleep(1)
                continue
            if health.status_code == 200:
                break
            time.sleep(1)
        else:
            pytest.fail("Local Functions host did not become ready within 90 seconds.")
        assert health.json() == {"status": "ok"}
        initial = client.get("/items")
        assert initial.status_code == 200
        assert len(initial.json()) == 2
        created = client.post("/items", json={"name": " functions-host-item "})
        assert created.status_code == 201
        assert created.json() == {"id": 3, "name": "functions-host-item"}
        after = client.get("/items")
        assert after.status_code == 200
        assert len(after.json()) == 3
        assert after.json()[-1] == created.json()
        invalid = client.post("/items", json={"name": ""})
        assert invalid.status_code == 422
        unchanged = client.get("/items")
        assert unchanged.status_code == 200
        assert unchanged.json() == after.json()
        assert client.get("/not-a-route").status_code == 404
