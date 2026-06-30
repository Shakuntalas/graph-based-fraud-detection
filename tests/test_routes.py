import json

from backend.config import ADMIN_PASSWORD, ADMIN_USERNAME


def test_register_and_login(client):
    response = client.post(
        "/api/register",
        data=json.dumps({"username": "testuser", "password": "testpass"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["registered"] is True
    assert data["user"]["username"] == "testuser"

    response = client.post(
        "/api/login",
        data=json.dumps({"username": "testuser", "password": "testpass"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["authenticated"] is True
    assert data["user"]["username"] == "testuser"


def test_user_status_unauthenticated(client):
    response = client.get("/api/user/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["authenticated"] is False
    assert data["user"] is None


def test_predict_transaction_without_login(client):
    response = client.post(
        "/api/predict",
        data=json.dumps({"sender": "C123", "receiver": "C456", "amount": 1000.0, "type": "PAYMENT"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "fraud_prediction" in data
    assert "fraud_probability" in data
    assert data["type"] == "PAYMENT"
    assert data["sender"] == "C123"


def test_admin_login_and_status(client):
    response = client.post(
        "/api/admin/login",
        data=json.dumps({"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}),
        content_type="application/json",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["authenticated"] is True

    status_response = client.get("/api/admin/status")
    assert status_response.status_code == 200
    status_data = status_response.get_json()
    assert status_data["authenticated"] is True


def test_admin_login_failure(client):
    response = client.post(
        "/api/admin/login",
        data=json.dumps({"username": "wrong", "password": "wrongpass"}),
        content_type="application/json",
    )

    assert response.status_code == 401
    data = response.get_json()
    assert data["authenticated"] is False
    assert "error" in data


def test_admin_transactions_requires_auth(client):
    response = client.get("/api/admin/transactions")
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Admin login required"
