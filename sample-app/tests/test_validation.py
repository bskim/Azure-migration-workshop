import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"name": ""},
        {"name": "   "},
        {"name": "x" * 81},
        {"name": 123},
        {"name": None},
        {"name": "valid", "extra": "not-allowed"},
    ],
)
def test_invalid_input_does_not_change_data(
    client: TestClient, payload: dict[str, object]
) -> None:
    before = client.get("/items").json()
    response = client.post("/items", json=payload)
    assert response.status_code == 422
    assert response.json()["detail"]
    assert client.get("/items").json() == before
