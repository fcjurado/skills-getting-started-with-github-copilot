import pytest


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class", 
                              "Basketball Team", "Tennis Club", "Art Studio", 
                              "Music Band", "Science Club", "Debate Team"]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        for activity_name in expected_activities:
            assert activity_name in data
    
    def test_get_activities_contains_required_fields(self, client, reset_activities):
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        for activity in data.values():
            for field in required_fields:
                assert field in activity


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "newemail@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    
    def test_signup_activity_not_found(self, client, reset_activities):
        # Arrange
        activity_name = "NonExistent Club"
        email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_duplicate_email(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_at_capacity(self, client, reset_activities):
        # Arrange
        # Basketball Team has max_participants=15 and 1 participant
        activity_name = "Basketball Team"
        # Add participants until at capacity
        from src.app import activities as app_activities
        activity = app_activities[activity_name]
        for i in range(activity["max_participants"] - 1):
            activity["participants"].append(f"email{i}@test.edu")
        
        # Try to add one more
        email = "extra@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "maximum capacity" in response.json()["detail"]
    
    def test_signup_adds_participant_to_list(self, client, reset_activities):
        # Arrange
        activity_name = "Art Studio"
        email = "newstudent@mergington.edu"
        from src.app import activities as app_activities
        initial_count = len(app_activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert len(app_activities[activity_name]["participants"]) == initial_count + 1
        assert email in app_activities[activity_name]["participants"]


class TestUnregisterEndpoint:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    
    def test_unregister_activity_not_found(self, client, reset_activities):
        # Arrange
        activity_name = "NonExistent Club"
        email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_email_not_registered(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_removes_participant_from_list(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        from src.app import activities as app_activities
        initial_count = len(app_activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert len(app_activities[activity_name]["participants"]) == initial_count - 1
        assert email not in app_activities[activity_name]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client, reset_activities):
        # Arrange - TestClient follows redirects by default
        
        # Act
        response = client.get("/", follow_redirects=True)
        
        # Assert
        assert response.status_code == 200
