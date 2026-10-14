import json
import os
from pathlib import Path
from urllib.parse import urlsplit

import httpx
import pytest


@pytest.mark.skipif(
    not os.environ.get("WORKSHOP_FUNCTIONS_CLOUD_URL"),
    reason="Set the approved fresh Function App URL and protected function-level key file.",
)
def test_cloud_function_key_and_bounded_http_contract():
    if os.environ.get("WORKSHOP_CLOUD_WRITE_APPROVED") != "1":
        pytest.fail("Explicit synthetic-write approval required.")
    endpoint = os.environ["WORKSHOP_FUNCTIONS_CLOUD_URL"]
    parsed = urlsplit(endpoint)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or not parsed.hostname.startswith("func-amw-")
        or not parsed.hostname.endswith(".azurewebsites.net")
        or parsed.username
        or parsed.password
        or parsed.port not in (None, 443)
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Use the exact approved lab HTTPS Function App endpoint.")
    key_path = os.environ.get("WORKSHOP_FUNCTIONS_KEY_FILE")
    if not key_path:
        pytest.fail("A protected function-level key file is required; do not put keys in argv.")
    key = Path(key_path).read_text(encoding="utf-8-sig").strip()
    if not key:
        pytest.fail("The protected function key file is empty.")
    with httpx.Client(base_url=endpoint, timeout=60) as client:
        assert client.get("/health").status_code == 401
        assert client.get("/health", headers={"x-functions-key": "invalid-workshop-key"}).status_code == 401
        client.headers["x-functions-key"] = key
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json() == {"status": "ok"}
        initial = client.get("/items")
        assert initial.status_code == 200
        assert initial.json() == [
            {"id": 1, "name": "sample-one"},
            {"id": 2, "name": "sample-two"},
        ]
        created = client.post("/items", json={"name": " functions-cloud-item "})
        assert created.status_code == 201
        assert created.json() == {"id": 3, "name": "functions-cloud-item"}
        after = client.get("/items")
        assert after.status_code == 200
        assert after.json() == initial.json() + [created.json()]
        invalid = client.post("/items", json={"name": ""})
        assert invalid.status_code == 422
        unchanged = client.get("/items")
        assert unchanged.status_code == 200
        assert unchanged.json() == after.json()
        assert client.get("/not-a-route").status_code == 404
        print(
            json.dumps(
                {
                    "no_key": 401,
                    "wrong_key": 401,
                    "function_key_health": 200,
                    "post": 201,
                    "invalid": 422,
                    "bounded_read_back": True,
                    "missing_route": 404,
                }
            )
        )
