from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Debate Team" in activities  # It's "Debate Team" not "Debate Club"

def test_signup_for_activity():
    activity = "Chess Club"
    email = "test@example.com"
    
    # First signup should succeed
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    
    # Second signup should fail (duplicate)
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_unregister_from_activity():
    activity = "Chess Club"
    email = "test@example.com"
    
    # First, sign up for the activity
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Now unregister
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Successfully unregistered from {activity}"
    
    # Verify the participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]

def test_signup_invalid_activity():
    response = client.post("/activities/InvalidClub/signup?email=test@example.com")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_max_participants():
    activity = "Chess Club"
    # Try to sign up more participants than allowed
    for i in range(15):
        email = f"test{i}@example.com"
        response = client.post(f"/activities/{activity}/signup?email={email}")
        if i >= 12:  # Chess Club has max 12 participants
            assert response.status_code == 400
            assert "Activity is full" in response.json()["detail"]
            break