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


def test_signup_for_activity_normalizes_email_before_duplicate_check():
    first_email = " New.Student@Mergington.edu "

    first_response = client.post("/activities/Chess%20Club/signup", params={"email": first_email})
    assert first_response.status_code == 200

    second_response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "new.student@mergington.edu"},
    )

    assert second_response.status_code == 400
    assert second_response.json() == {"detail": "Student is already signed up"}
    participants = activities["Chess Club"]["participants"]

    assert participants.count("new.student@mergington.edu") == 1
    assert first_email not in participants
    assert all(participant == participant.strip().lower() for participant in participants)


def test_signup_for_activity_rejects_when_activity_is_full():
    activities["Chess Club"]["max_participants"] = len(activities["Chess Club"]["participants"])

    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "new.student@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}
