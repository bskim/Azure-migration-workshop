from fastapi.testclient import TestClient

from app import MAX_ITEMS, create_app


def test_seed_write_and_read_back(client: TestClient) -> None:
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "sample-one"},
        {"id": 2, "name": "sample-two"},
    ]
    created = client.post("/items", json={"name": " workshop-item "})
    assert created.status_code == 201
    assert created.json() == {"id": 3, "name": "workshop-item"}
    assert client.get("/items").json()[-1] == created.json()


def test_new_app_resets_in_memory_data(client: TestClient) -> None:
    assert client.post("/items", json={"name": "temporary"}).status_code == 201
    assert len(client.get("/items").json()) == 3
    with TestClient(create_app()) as restarted:
        assert len(restarted.get("/items").json()) == 2


def test_capacity_failure_does_not_change_data(client: TestClient) -> None:
    for index in range(MAX_ITEMS - 2):
        assert client.post("/items", json={"name": f"item-{index}"}).status_code == 201
    response = client.post("/items", json={"name": "over-capacity"})
    assert response.status_code == 409
    assert response.json() == {"detail": "Workshop item limit reached."}
    assert len(client.get("/items").json()) == MAX_ITEMS
