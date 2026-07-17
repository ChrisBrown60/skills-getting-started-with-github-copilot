"""Tests for the Mergington High School Activities API."""

import pytest
from urllib.parse import quote
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a clean state before each test."""
    original = {name: {**details, "participants": list(details["participants"])}
                for name, details in activities.items()}
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_200(self):
        # Arrange / Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        # Arrange / Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert isinstance(data, dict)

    def test_get_activities_contains_expected_keys(self):
        # Arrange / Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity in data.values():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity


class TestSignupForActivity:
    def test_signup_success(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{quote(activity_name, safe='')}/signup", params={"email": email})
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert email in data["message"]

    def test_signup_adds_participant(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        client.post(f"/activities/{quote(activity_name, safe='')}/signup", params={"email": email})

        # Assert
        assert email in activities[activity_name]["participants"]

    def test_signup_activity_not_found(self):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{quote(activity_name, safe='')}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404

    def test_signup_duplicate_rejected(self):
        # Arrange
        activity_name = "Chess Club"
        email = "duplicate@mergington.edu"
        client.post(f"/activities/{quote(activity_name, safe='')}/signup", params={"email": email})

        # Act
        response = client.post(f"/activities/{quote(activity_name, safe='')}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400


class TestUnregisterFromActivity:
    def test_unregister_success(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/{quote(activity_name, safe='')}/unregister", params={"email": email})
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert email in data["message"]

    def test_unregister_removes_participant(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        client.delete(f"/activities/{quote(activity_name, safe='')}/unregister", params={"email": email})

        # Assert
        assert email not in activities[activity_name]["participants"]

    def test_unregister_activity_not_found(self):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{quote(activity_name, safe='')}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 404

    def test_unregister_not_enrolled(self):
        # Arrange
        activity_name = "Chess Club"
        email = "notenrolled@mergington.edu"

        # Act
        response = client.delete(f"/activities/{quote(activity_name, safe='')}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 400
