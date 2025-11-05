import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def client():
    # Backup the shared in-memory activities dict and restore after each test
    original = copy.deepcopy(activities)
    with TestClient(app) as c:
        yield c
    activities.clear()
    activities.update(original)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # ensure a known activity exists
    assert "Chess Club" in data


def test_signup_and_unregister_flow(client):
    activity = "Chess Club"
    email = "testuser@example.com"

    # Ensure clean state
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")
    assert email in activities[activity]["participants"]

    # Unregister
    resp2 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert "Unregistered" in body2.get("message", "")
    assert email not in activities[activity]["participants"]


def test_signup_duplicate_returns_400(client):
    activity = "Programming Class"
    # pick an existing participant
    existing = activities[activity]["participants"][0]
    resp = client.post(f"/activities/{activity}/signup?email={existing}")
    assert resp.status_code == 400


def test_unregister_not_signed_returns_404(client):
    activity = "Chess Club"
    email = "not-registered@example.com"
    # Ensure email is not in participants
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 404
