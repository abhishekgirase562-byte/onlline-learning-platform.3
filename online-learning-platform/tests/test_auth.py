import json

def test_register_success(client):
    res = client.post("/api/auth/register", json={
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "Password123!",
        "role": "student"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert data["user"]["email"] == "jane@example.com"
    assert "password_hash" not in data["user"]


def test_register_duplicate_email(client):
    res = client.post("/api/auth/register", json={
        "name": "Duplicate Sarah",
        "email": "student@learnhub.com",
        "password": "Password123!"
    })
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False
    assert "already exists" in data["message"].lower()


def test_login_success(client):
    res = client.post("/api/auth/login", json={
        "email": "student@learnhub.com",
        "password": "Student@12345"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["user"]["role"] == "student"


def test_login_invalid_password(client):
    res = client.post("/api/auth/login", json={
        "email": "student@learnhub.com",
        "password": "WrongPassword!"
    })
    assert res.status_code == 401
    data = res.get_json()
    assert data["success"] is False


def test_auth_me_and_logout(client):
    # Log in first
    client.post("/api/auth/login", json={
        "email": "admin@learnhub.com",
        "password": "Admin@12345"
    })

    # Check /api/auth/me
    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    me_data = me_res.get_json()
    assert me_data["authenticated"] is True
    assert me_data["user"]["role"] == "admin"

    # Logout
    logout_res = client.post("/api/auth/logout")
    assert logout_res.status_code == 200

    # Check /api/auth/me after logout
    after_me = client.get("/api/auth/me")
    assert after_me.get_json()["authenticated"] is False
