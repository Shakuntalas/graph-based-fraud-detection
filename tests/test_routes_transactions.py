import networkx as nx

from backend import runtime
from backend.factory import create_app
from backend.routes import transactions as transaction_routes


class DummyAnomalyDetector:
    def score(self, amount):
        return {"is_anomaly": amount > 100000, "anomaly_score": -0.5}

    def add_amount(self, amount):
        self.last_amount = amount


def test_predict_route_saves_transaction_and_returns_explanation(isolated_database, monkeypatch):
    app = create_app(load_artifacts=False)
    app.config.update(TESTING=True)
    client = app.test_client()

    monkeypatch.setattr(runtime, "load_runtime_artifacts", lambda: None)
    monkeypatch.setattr(runtime, "TRANSACTION_GRAPH", nx.DiGraph())
    monkeypatch.setattr(runtime, "MODEL", object())
    monkeypatch.setattr(runtime, "FEATURE_COLUMNS", ["amount"])
    monkeypatch.setattr(runtime, "FRAUD_THRESHOLD", 0.2)
    monkeypatch.setattr(runtime, "ANOMALY_DETECTOR", DummyAnomalyDetector())
    monkeypatch.setattr(
        transaction_routes,
        "predict_transaction",
        lambda **kwargs: {"fraud_prediction": 1, "fraud_probability": 0.3, "threshold": 0.2},
    )
    monkeypatch.setattr(transaction_routes, "export_graph_html", lambda *args, **kwargs: (None, []))

    response = client.post("/api/predict", json={
        "sender": "C1",
        "receiver": "M1",
        "amount": 250000,
        "type": "TRANSFER",
    })

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["fraud_prediction"] == 1
    assert payload["risk_level"] in {"MEDIUM", "HIGH", "CRITICAL"}
    assert payload["explanation"]["reasons"]


def test_predict_route_rejects_bad_amount(isolated_database):
    app = create_app(load_artifacts=False)
    app.config.update(TESTING=True)
    response = app.test_client().post("/api/predict", json={
        "sender": "C1",
        "receiver": "M1",
        "amount": 0,
    })
    assert response.status_code == 400
