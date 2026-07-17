import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


client = TestClient(app)


def test_signup_for_activity_rejects_duplicate_student():
    email = "new.student@mergington.edu"

    first_response = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert first_response.status_code == 200

    second_response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    assert second_response.status_code == 400
    assert second_response.json() == {"detail": "Student is already signed up"}


def test_signup_for_activity_adds_new_student():
    email = "new.student@mergington.edu"

    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]
