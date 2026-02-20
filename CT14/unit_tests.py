import numpy as np
import ast
import networkx as nx
import pytest


def _graph_from_adjacency(A):
    A = np.array(A, dtype=int)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        pytest.fail("Adjacency matrix must be square.")
    if not np.all((A == 0) | (A == 1)):
        pytest.fail("Adjacency matrix entries must be 0/1.")
    if not np.all(A == A.T):
        pytest.fail("Adjacency matrix must be symmetric (simple undirected graph).")
    if np.any(np.diag(A) != 0):
        pytest.fail("Adjacency matrix must have zero diagonal (no loops).")
    n = A.shape[0]
    G = nx.Graph()
    G.add_nodes_from(range(n))
    rows, cols = np.where(np.triu(A, 1) == 1)
    for u, v in zip(rows.tolist(), cols.tolist()):
        G.add_edge(int(u), int(v))
    return G, n


def _graph_from_edge_list(E):
    V = set(); edges = []; seen = set()
    for e in E:
        if not (isinstance(e, (list, tuple)) and len(e) == 2):
            pytest.fail("Each edge must be a 2-list/tuple [u, v].")
        u, v = int(e[0]), int(e[1])
        if u == v:
            pytest.fail("No loops allowed (u != v).")
        a, b = (u, v) if u < v else (v, u)
        if (a, b) in seen:
            pytest.fail("Multiple edges detected; graph must be simple.")
        seen.add((a, b))
        edges.append((u, v))
        V.add(u); V.add(v)
    n = max(V) + 1 if V else 0
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)
    return G, n


def _parse_construction(obj):
    if isinstance(obj, str):
        try:
            obj = ast.literal_eval(obj)
        except Exception as e:
            pytest.fail(f"Could not parse string construction: {e}")
    if isinstance(obj, dict):
        if "edges" in obj:
            return _graph_from_edge_list(obj["edges"])
        elif "adjacency" in obj:
            return _graph_from_adjacency(obj["adjacency"])
        else:
            pytest.fail("Dict construction must have 'edges' or 'adjacency' key.")
    if isinstance(obj, (list, tuple)):
        if len(obj) == 0:
            pytest.fail("Empty construction.")
        if isinstance(obj[0], (list, tuple)) and len(obj[0]) == 2 and not any(isinstance(x, (list, tuple)) and len(x) != 2 for x in obj):
            return _graph_from_edge_list(obj)
        return _graph_from_adjacency(obj)
    pytest.fail("Unsupported construction type. Use adjacency matrix or edge list.")


def test_graph_properties_and_connectivity(construction, parameters):
    G, N = _parse_construction(construction)
    n = int(parameters.get("n", 1))
    target_N = 4 * n
    assert N == target_N, f"Incorrect. The graph must have 4n={target_N} vertices, found {N}."
    assert nx.is_connected(G), "Incorrect. The graph must be connected."
    degrees = [deg for _, deg in G.degree()]
    assert all(d == 3 for d in degrees), f"Incorrect. The graph must be 3-regular; degrees found: {sorted(set(degrees))}."
    kappa = nx.node_connectivity(G)
    assert kappa == 2, f"Incorrect. Vertex connectivity must be 2. Found κ(G)={kappa}."
