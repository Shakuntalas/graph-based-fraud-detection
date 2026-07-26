import networkx as nx

from backend.services.graph_intelligence import analyze_graph


def test_analyze_graph_returns_suspicious_communities():
    graph = nx.DiGraph()
    graph.add_edge("C1", "C2", weight=500)
    graph.add_edge("C2", "C3", weight=600)
    graph.add_edge("C3", "C1", weight=700)
    graph.add_edge("C4", "C5", weight=10)

    result = analyze_graph(graph, account_risks={"C1": 90, "C2": 70, "C3": 60})

    assert result["betweenness"]
    assert result["node_community"]["C1"]
    assert result["communities"][0]["suspicious"] is True
    assert result["communities"][0]["cluster_risk"] >= 50


def test_analyze_empty_graph_returns_empty_summary():
    result = analyze_graph(nx.DiGraph())
    assert result == {"betweenness": {}, "communities": [], "node_community": {}}
