"""API integration tests."""

from tests.conftest import HEADERS


def test_health_check(client):
    """Health endpoint returns 200 without auth."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_user(client):
    """Creating a user returns 201 and the user data."""
    payload = {
        "email": "alice@example.com",
        "username": "alice",
        "full_name": "Alice Smith",
    }
    response = client.post("/api/v1/users/", json=payload, headers=HEADERS)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["username"] == "alice"
    assert data["is_active"] is True


def test_list_users_empty(client):
    """Listing users on an empty DB returns an empty list."""
    response = client.get("/api/v1/users/", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_create_task(client):
    """Creating a task returns 201 with correct defaults."""
    user_resp = client.post(
        "/api/v1/users/",
        json={"email": "bob@example.com", "username": "bob", "full_name": "Bob Jones"},
        headers=HEADERS,
    )
    user_id = user_resp.json()["id"]

    task_resp = client.post(
        "/api/v1/tasks/",
        json={"title": "Write tests", "owner_id": user_id},
        headers=HEADERS,
    )
    assert task_resp.status_code == 201
    task_data = task_resp.json()
    assert task_data["title"] == "Write tests"
    assert task_data["status"] == "pending"
    assert task_data["priority"] == "medium"


def test_unauthorized_access(client):
    """Requests without a valid API key are rejected."""
    response = client.get("/api/v1/users/")
    assert response.status_code == 422  # missing header

    response = client.get("/api/v1/users/", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 403


def test_user_not_found(client):
    """Requesting a non-existent user returns 404."""
    response = client.get("/api/v1/users/999", headers=HEADERS)
    assert response.status_code == 404


def test_update_and_delete_task(client):
    """Tasks can be updated and deleted through the API."""
    user_resp = client.post(
        "/api/v1/users/",
        json={"email": "carol@example.com", "username": "carol", "full_name": "Carol White"},
        headers=HEADERS,
    )
    user_id = user_resp.json()["id"]

    task_resp = client.post(
        "/api/v1/tasks/",
        json={"title": "Initial title", "owner_id": user_id},
        headers=HEADERS,
    )
    task_id = task_resp.json()["id"]

    # Update
    update_resp = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Updated title", "status": "in_progress"},
        headers=HEADERS,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Updated title"
    assert update_resp.json()["status"] == "in_progress"

    # Delete
    delete_resp = client.delete(f"/api/v1/tasks/{task_id}", headers=HEADERS)
    assert delete_resp.status_code == 204

    # Verify gone
    get_resp = client.get(f"/api/v1/tasks/{task_id}", headers=HEADERS)
    assert get_resp.status_code == 404
