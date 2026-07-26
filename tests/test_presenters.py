from backend.presenters import format_transaction, public_user


def test_presenters_hide_password_and_parse_explanations():
    user = {
        "id": 1,
        "username": "alice",
        "password_hash": "secret",
        "account_id": "C100000001",
        "created_at": "2026-01-01T00:00:00+00:00",
    }
    assert "password_hash" not in public_user(user)

    transaction = {
        "id": 7,
        "created_at": "2026-01-01T00:00:00+00:00",
        "sender": "C1",
        "receiver": "M1",
        "amount": 1000,
        "transaction_type": "PAYMENT",
        "prediction": 0,
        "probability": 0.35,
        "risk_level": None,
        "explanation": "{\"reasons\": [\"Test reason\"]}",
        "anomaly_score": -0.1,
        "username": "alice",
    }

    formatted = format_transaction(transaction)
    assert formatted["risk_level"] == "MEDIUM"
    assert formatted["explanation"]["reasons"] == ["Test reason"]
