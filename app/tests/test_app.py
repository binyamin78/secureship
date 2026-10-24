import pytest

from devboard import create_app


@pytest.fixture
def client():
    return create_app().test_client()


def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_create_and_list_notes(client):
    res = client.post("/api/notes", json={"author": "dana", "text": "shipping v2"})
    assert res.status_code == 201
    texts = [n["text"] for n in client.get("/api/notes").get_json()]
    assert "shipping v2" in texts


def test_create_note_requires_text(client):
    assert client.post("/api/notes", json={"author": "x"}).status_code == 400


def test_index_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"DevBoard" in res.data


def test_work_endpoint(client):
    res = client.get("/api/work?rounds=10")
    assert res.status_code == 200
    assert res.get_json()["rounds"] == 10


def test_metrics_endpoint(client):
    client.get("/api/health")
    res = client.get("/metrics")
    assert res.status_code == 200
    assert b"devboard_http_requests_total" in res.data
