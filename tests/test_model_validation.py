import numpy as np
import pandas as pd
import pytest

from src import model


class ProbabilityModel:
    def predict_proba(self, frame):
        return np.array([
            [0.95, 0.05],
            [0.85, 0.15],
            [0.70, 0.30],
            [0.20, 0.80],
        ])


def test_evaluate_model_selects_threshold_and_reports_auc(monkeypatch):
    monkeypatch.setattr(model, "save_evaluation_plots", lambda *args: None)
    metrics = model.evaluate_model(
        ProbabilityModel(),
        pd.DataFrame({"amount": [1, 2, 3, 4]}),
        pd.Series([0, 0, 1, 1]),
    )

    assert metrics["best_threshold"] in model.THRESHOLD_CANDIDATES
    assert metrics["roc_auc"] == pytest.approx(1.0)
    assert metrics["confusion_matrix"]


def test_create_balanced_dataset_rejects_missing_fraud_rows():
    data = pd.DataFrame({"isFraud": [0, 0, 0], "amount": [1, 2, 3]})
    with pytest.raises(ValueError):
        model.create_balanced_dataset(data)
