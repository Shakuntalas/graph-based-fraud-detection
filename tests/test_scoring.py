from backend.services.database import create_user, save_transaction
from backend.services.scoring import adjust_runtime_probability, generate_alerts, get_risky_accounts


def test_runtime_probability_and_alerts_use_reasons(isolated_database):
    ok, _, user = create_user("sender", "StrongPass1")
    assert ok is True

    for index in range(3):
        save_transaction(
            user_id=user["id"],
            sender=user["account_id"],
            receiver=f"M{index}",
            amount=100 + index,
            transaction_type="PAYMENT",
            probability=0.1,
            prediction=0,
        )

    probability = adjust_runtime_probability(
        model_probability=0.05,
        sender=user["account_id"],
        amount=600000,
        transaction_type="TRANSFER",
        is_anomaly=True,
    )
    assert probability >= 0.62

    transaction = save_transaction(
        user_id=user["id"],
        sender=user["account_id"],
        receiver="M9",
        amount=600000,
        transaction_type="TRANSFER",
        probability=probability,
        prediction=1,
        explanation={"reasons": ["Large transaction amount"]},
    )
    alerts = generate_alerts(transaction, is_anomaly=True)

    assert {alert["type"] for alert in alerts} >= {
        "High-risk transaction detected",
        "Large transaction anomaly",
        "Suspicious account cluster",
    }
    assert "Large transaction amount" in alerts[0]["message"]
    assert user["account_id"] in get_risky_accounts()
