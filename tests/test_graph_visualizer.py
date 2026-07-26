import networkx as nx

from backend.services import graph_visualizer


def test_export_graph_html_writes_graph_and_clusters(tmp_path, monkeypatch):
    graph = nx.DiGraph()
    graph.add_edge("C1", "C2", weight=100000)
    graph.add_edge("C2", "C3", weight=120000)

    output = tmp_path / "graph.html"
    monkeypatch.setattr(graph_visualizer, "GRAPH_DIR", tmp_path)
    monkeypatch.setattr(graph_visualizer, "GRAPH_PATH", output)

    path, clusters = graph_visualizer.export_graph_html(
        graph,
        risky_accounts={"C1"},
        account_reputations=[
            {"account_id": "C1", "account_risk_score": 90, "transaction_count": 4},
            {"account_id": "C2", "account_risk_score": 75, "transaction_count": 3},
        ],
    )

    assert path == output
    assert output.exists()
    assert clusters
