import os
import time
from urllib.parse import urlsplit

import httpx
import pytest


@pytest.mark.skipif(
    not os.environ.get("WORKSHOP_CONTAINER_APP_URL"),
    reason="Set WORKSHOP_CONTAINER_APP_URL to this lab's new approved app.",
)
def test_approved_cloud_app_health_write_read_and_validation():
    if os.environ.get("WORKSHOP_CLOUD_WRITE_APPROVED") != "1":
        pytest.fail("Explicit synthetic-write approval required: WORKSHOP_CLOUD_WRITE_APPROVED=1.")
    endpoint = os.environ["WORKSHOP_CONTAINER_APP_URL"]
    parsed = urlsplit(endpoint)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or not parsed.hostname.endswith(".azurecontainerapps.io")
        or not parsed.hostname.startswith("app-amw-")
        or parsed.username
        or parsed.password
        or parsed.port not in (None, 443)
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Use the exact approved lab HTTPS Container App URL.")
    with httpx.Client(base_url=endpoint, timeout=10) as client:
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
            pytest.fail("Approved cloud app did not become healthy within 90 seconds.")
        assert health.json() == {"status": "ok"}
        before = client.get("/items")
        assert before.status_code == 200
        assert before.json() == [
            {"id": 1, "name": "sample-one"},
            {"id": 2, "name": "sample-two"},
        ]
        created = client.post("/items", json={"name": " azure-workshop-item "})
        assert created.status_code == 201
        assert created.json() == {"id": 3, "name": "azure-workshop-item"}
        after = client.get("/items")
        assert after.status_code == 200
        assert after.json() == before.json() + [created.json()]
        invalid = client.post("/items", json={"name": ""})
        assert invalid.status_code == 422
        unchanged = client.get("/items")
        assert unchanged.status_code == 200
        assert unchanged.json() == after.json()
        assert client.get("/not-a-route").status_code == 404
