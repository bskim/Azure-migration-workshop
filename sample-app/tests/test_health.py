from fastapi.testclient import TestClient


def test_health_and_unknown_route(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert client.get("/unknown").status_code == 404
    assert client.get("/health").json() == {"status": "ok"}
