import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Snapshot and restore the in-memory activities around each test."""
    original = copy.deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(original)


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    # basic sanity check
    assert "Chess Club" in data


def test_signup_success():
    email = "testuser@example.com"
    activity = "Chess Club"
    path = f"/activities/{quote(activity)}/signup"

    # ensure clean start
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    r = client.post(path, params={"email": email})
    assert r.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_duplicate():
    email = "dup@example.com"
    activity = "Programming Class"
    path = f"/activities/{quote(activity)}/signup"

    # add participant first
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)

    r = client.post(path, params={"email": email})
    assert r.status_code == 400


def test_unregister_participant():
    email = "remove@example.com"
    activity = "Gym Class"
    del_path = f"/activities/{quote(activity)}/participants"

    # ensure participant present
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)

    r = client.delete(del_path, params={"email": email})
    assert r.status_code == 200
    assert email not in activities[activity]["participants"]
