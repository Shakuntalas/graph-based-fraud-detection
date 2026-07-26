import joblib
import networkx as nx

from backend import runtime
from backend.config import ADMIN_PASSWORD, ADMIN_USERNAME
from backend.factory import create_app
from backend.services.database import create_user, save_transaction, update_account_reputation


def test_admin_dashboard_returns_validation_and_analytics(isolated_database, tmp_path, monkeypatch):
    app = create_app(load_artifacts=False)
    app.config.update(TESTING=True)
    client = app.test_client()

    ok, _, user = create_user("adminview", "StrongPass1")
    assert ok is True
    transaction = save_transaction(
        user_id=user["id"],
        sender=user["account_id"],
        receiver="M1",
        amount=250000,
        transaction_type="TRANSFER",
        probability=0.8,
        prediction=1,
        risk_level="CRITICAL",
        explanation={"reasons": ["Large transaction amount"]},
    )
    update_account_reputation(user["account_id"], transaction["amount"], 0.8, 1, True)

    models_dir = tmp_path / "models"
    models_dir.mkdir()
    (models_dir / "feature_importance.json").write_text(
        "[{\"feature\": \"amount\", \"importance\": 0.9}]",
        encoding="utf-8",
    )
    joblib.dump({"f1_score": 0.8, "roc_auc": 0.9}, models_dir / "model_metadata.pkl")
    monkeypatch.setattr("backend.routes.admin.PROJECT_ROOT", tmp_path)

    graph = nx.DiGraph()
    graph.add_edge(user["account_id"], "M1", weight=250000)
    monkeypatch.setattr(runtime, "TRANSACTION_GRAPH", graph)

    login = client.post("/api/admin/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    assert login.status_code == 200

    response = client.get("/api/admin/transactions")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["metrics"]["flagged"] == 1
    assert payload["feature_importance"][0]["feature"] == "amount"
    assert payload["model_validation"]["roc_auc"] == 0.9
    assert payload["analytics"]["transaction_distribution"]
