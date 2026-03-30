def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_expected_structure(client):
    # Arrange
    expected_fields = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0

    first_activity = next(iter(data.values()))
    assert expected_fields.issubset(first_activity.keys())


def test_signup_adds_new_participant(client):
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    before_count = len(client.get("/activities").json()[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"

    updated_participants = client.get("/activities").json()[activity_name]["participants"]
    assert len(updated_participants) == before_count + 1
    assert new_email in updated_participants


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    new_email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = "michael@mergington.edu"
    before_count = len(client.get("/activities").json()[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": duplicate_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"

    updated_participants = client.get("/activities").json()[activity_name]["participants"]
    assert len(updated_participants) == before_count


def test_unregister_removes_existing_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = "michael@mergington.edu"
    activities_before = client.get("/activities").json()
    before_count = len(activities_before[activity_name]["participants"])

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email_to_remove},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == (
        f"Unregistered {email_to_remove} from {activity_name}"
    )

    updated_participants = client.get("/activities").json()[activity_name]["participants"]
    assert len(updated_participants) == before_count - 1
    assert email_to_remove not in updated_participants


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email_to_remove = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email_to_remove},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_missing_participant(client):
    # Arrange
    activity_name = "Chess Club"
    activities_before = client.get("/activities").json()
    before_count = len(activities_before[activity_name]["participants"])

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not signed up for this activity"

    updated_participants = client.get("/activities").json()[activity_name]["participants"]
    assert len(updated_participants) == before_count
