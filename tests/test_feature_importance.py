import json

from src import feature_importance


class ImportanceModel:
    feature_importances_ = [0.2, 0.7, 0.1]


def test_generate_feature_importance_writes_sorted_outputs(tmp_path, monkeypatch):
    output_png = tmp_path / "feature_importance.png"
    output_json = tmp_path / "feature_importance.json"
    monkeypatch.setattr(feature_importance, "GRAPHS_DIR", tmp_path)
    monkeypatch.setattr(feature_importance, "FEATURE_IMPORTANCE_PATH", output_png)
    monkeypatch.setattr(feature_importance, "FEATURE_IMPORTANCE_DATA_PATH", output_json)

    records = feature_importance.generate_feature_importance(
        model=ImportanceModel(),
        feature_columns=["amount", "pagerank", "degree"],
        top_n=3,
    )

    assert records[0]["feature"] == "pagerank"
    assert output_png.exists()
    assert json.loads(output_json.read_text(encoding="utf-8"))[0]["feature"] == "pagerank"
