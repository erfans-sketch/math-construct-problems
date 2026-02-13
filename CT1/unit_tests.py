import numpy as np
import ast
import json
import pytest


def _edges_from_adjacency(A):
    n = A.shape[0]
    E = []
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] == 1:
                E.append((i, j))
    return E


def _adjacency_from_VE(V, E):
    n = len(V)
    index = {v: i for i, v in enumerate(V)}
    A = np.zeros((n, n), dtype=int)
    for (u, v) in E:
        if u not in index or v not in index:
            raise ValueError("Edge uses a vertex not present in V")
        i, j = index[u], index[v]
        if i == j:
            raise ValueError("Self-loop detected in E")
        A[i, j] = 1
        A[j, i] = 1
    return A


def _is_simple_undirected(A):
    if A.shape[0] != A.shape[1]:
        return False, "Adjacency matrix is not square"
    if not np.array_equal(A, A.astype(int)):
        return False, "Adjacency contains non-integer entries"
    if not np.all((A == 0) | (A == 1)):
        return False, "Adjacency must be 0/1"
    if not np.array_equal(A, A.T):
        return False, "Adjacency not symmetric (graph should be undirected)"
    if np.any(np.diag(A) != 0):
        return False, "Self-loops are not allowed (diagonal must be zero)"
    return True, ""


def _edge_in_k_cycle(A, edge, k):
    if k < 3:
        return False
    n = A.shape[0]
    i, j = edge
    if i == j:
        return False
    if i > j:
        i, j = j, i
    if not (0 <= i < n and 0 <= j < n) or A[i, j] != 1:
        return False
    neighbors = [np.flatnonzero(A[v]).tolist() for v in range(n)]
    target = i
    start = j
    steps_left = k - 1
    visited = set([i, j])

    def dfs(cur, remaining):
        if remaining == 0:
            return cur == target
        for w in neighbors[cur]:
            if remaining == 1:
                if w == target:
                    return True
                continue
            if w == target or w in visited:
                continue
            visited.add(w)
            if dfs(w, remaining - 1):
                return True
            visited.remove(w)
        return False

    return dfs(start, steps_left)


def _has_cycle_of_length_k(A, k):
    if k < 3:
        return False, None
    n = A.shape[0]
    if k > n:
        return False, None
    neighbors = [np.flatnonzero(A[v]).tolist() for v in range(n)]
    for s in range(n):
        if len(neighbors[s]) < 2:
            continue
        visited = set([s])
        def dfs(cur, remaining, path):
            if remaining == 1:
                if A[cur, s] == 1:
                    return True, path[:]
                return False, None
            for w in neighbors[cur]:
                if w == s or w in visited:
                    continue
                visited.add(w)
                path.append(w)
                found, cyc = dfs(w, remaining - 1, path)
                if found:
                    return True, cyc
                path.pop()
                visited.remove(w)
            return False, None
        for v in neighbors[s]:
            visited.add(v)
            path = [s, v]
            found, cyc = dfs(v, k - 1, path)
            if found:
                return True, cyc
            visited.remove(v)
    return False, None


def _every_edge_in_cycles(A, lengths):
    n = A.shape[0]
    for k in lengths:
        if k < 3 or k > n:
            return False, f"Requested cycle length {k} is invalid for n={n}"
    edges = _edges_from_adjacency(A)
    for e in edges:
        for k in sorted(lengths):
            if not _edge_in_k_cycle(A, e, k):
                return False, f"Edge {e} is not contained in any simple cycle of length {k}"
    return True, "ok"


def _no_cycle_length_multiple_of(A, mod):
    if not isinstance(mod, int) or mod <= 0:
        return False, "mod must be a positive integer"
    n = A.shape[0]
    start = ((3 + mod - 1) // mod) * mod
    if start > n:
        return True, "ok"
    for k in range(start, n + 1, mod):
        found, cyc = _has_cycle_of_length_k(A, k)
        if found:
            return False, f"Found a simple cycle of length {k} (≡ 0 mod {mod}): {cyc}"
    return True, "ok"


def _parse_construction(construction):
    obj = construction
    if isinstance(obj, str):
        s = obj.strip()
        if s.startswith("```"):
            lines = s.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            s = "\n".join(lines).strip()
        parsed = None
        try:
            parsed = json.loads(s)
        except Exception:
            try:
                parsed = ast.literal_eval(s)
            except Exception:
                parsed = None
        if parsed is not None:
            obj = parsed
    if isinstance(obj, dict) and "V" in obj and "E" in obj:
        A = _adjacency_from_VE(obj["V"], obj["E"])
    else:
        A = np.array(obj, dtype=int)
        if A.ndim != 2 or A.shape[0] != A.shape[1]:
            pytest.fail("Adjacency matrix must be square")
    ok, msg = _is_simple_undirected(A)
    assert ok, msg
    return A


def test_cycle_requirements(construction, parameters):
    """
    Verify the constructed simple undirected graph satisfies the cycle constraints:
    every edge in the graph must participate in at least one simple cycle of the
    specified even length and one of the specified odd length, as provided via
    `parameters` (defaults: even_cycle=4, odd_cycle=5).
    """
    A = _parse_construction(construction)
    # New explicit non-triviality requirement: graph must contain at least one edge
    edges = _edges_from_adjacency(A)
    assert len(edges) >= 1, "Graph must contain at least one edge"
    even_cycle = int(parameters.get("even_cycle", 4))
    odd_cycle = int(parameters.get("odd_cycle", 5))
    ok, msg = _every_edge_in_cycles(A, lengths={even_cycle, odd_cycle})
    assert ok, msg


def test_no_multiple_of_mod_cycles(construction, parameters):
    """
    Ensure the graph has no simple cycles whose lengths are divisible by the
    provided modulus `mod` (default: 3). This guards against the presence of any
    cycle length that is a multiple of `mod`.
    """
    A = _parse_construction(construction)
    # Maintain non-triviality across all tests for clearer attribution
    edges = _edges_from_adjacency(A)
    assert len(edges) >= 1, "Graph must contain at least one edge"
    mod = int(parameters.get("mod", 3))
    ok, msg = _no_cycle_length_multiple_of(A, mod=mod)
    assert ok, msg

def test_nontrivial_graph(construction):
    """Explicit check that G is non-trivial (has at least one edge)."""
    A = _parse_construction(construction)
    edges = _edges_from_adjacency(A)
    assert len(edges) >= 1, "Graph must contain at least one edge"

