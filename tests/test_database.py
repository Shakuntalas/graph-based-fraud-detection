import pytest

from backend.services.database import create_user, authenticate_user, count_transactions_by_sender, save_transaction, list_transactions


def test_user_creation_and_authentication(client):
    ok, message, user = create_user("alice", "strongpass")
    assert ok is True
    assert user is not None
    assert user["username"] == "alice"

    authenticated_user = authenticate_user("alice", "strongpass")
    assert authenticated_user is not None
    assert authenticated_user["id"] == user["id"]


def test_transaction_persistence(client):
    ok, _, user = create_user("bob", "anotherpass")
    assert ok is True

    transaction = save_transaction(
        user_id=user["id"],
        sender=user["account_id"],
        receiver="C999999999",
        amount=1234.56,
        transaction_type="PAYMENT",
        probability=0.15,
        prediction=0,
        anomaly_score=0.05,
    )

    assert transaction["sender"] == user["account_id"]
    assert transaction["receiver"] == "C999999999"

    rows = list_transactions(user_id=user["id"])
    assert len(rows) == 1
    assert rows[0]["id"] == transaction["id"]


def test_count_transactions_by_sender(client):
    ok, _, user = create_user("carol", "mypass123")
    assert ok is True

    for _ in range(5):
        save_transaction(
            user_id=user["id"],
            sender=user["account_id"],
            receiver="C123000001",
            amount=10.0,
            transaction_type="TRANSFER",
            probability=0.01,
            prediction=0,
        )

    count = count_transactions_by_sender(user["account_id"], limit=10)
    assert count == 5
