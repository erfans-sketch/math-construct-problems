import numpy as np
import ast
import pytest


def _parse_matrix_string(s: str):
    try:
        obj = ast.literal_eval(s)
        arr = np.array(obj, dtype=float)
        if arr.ndim != 2:
            raise ValueError("Parsed object is not 2D")
        return arr.tolist()
    except Exception:
        pass
    text = s.strip()
    import re
    rows_raw = re.split(r'[;\n]+', text)
    matrix = []
    for row in rows_raw:
        row = row.strip()
        if not row:
            continue
        tokens = [t for t in re.split(r'[\,\s]+', row) if t]
        try:
            nums = [float(t) for t in tokens]
        except ValueError:
            pytest.fail("Non-numeric token in string")
        matrix.append(nums)
    if not matrix:
        pytest.fail("Empty matrix")
    width = len(matrix[0])
    if any(len(r) != width for r in matrix):
        pytest.fail("Rows have different lengths")
    return matrix


def _to_numeric_matrix(construction):
    if isinstance(construction, str):
        matrix = _parse_matrix_string(construction)
    else:
        matrix = construction
    return np.array(matrix, dtype=float)


def _is_zero_one_matrix(A: np.ndarray) -> bool:
    return np.all((A == 0) | (A == 1))


def _is_symmetric_zero_diag(A: np.ndarray) -> bool:
    return np.allclose(A, A.T) and np.all(np.diag(A) == 0)


def _parse_edge_list(obj_or_str, n: int):
    if isinstance(obj_or_str, str):
        s = obj_or_str.strip()
        try:
            obj = ast.literal_eval(s)
        except Exception as e:
            pytest.fail(f"Could not parse edge list: {e}")
    else:
        obj = obj_or_str
    if not isinstance(obj, (list, tuple)):
        pytest.fail("Edge list must be a list/tuple of pairs.")
    edges = []
    for e in obj:
        if not (isinstance(e, (list, tuple)) and len(e) == 2):
            pytest.fail(f"Invalid edge {e!r}. Expect pairs like (u,v).")
        u, v = e
        if not (isinstance(u, (int, np.integer)) and isinstance(v, (int, np.integer))):
            pytest.fail(f"Edge endpoints must be integers: {e!r}")
        if not (1 <= int(u) <= n and 1 <= int(v) <= n):
            pytest.fail(f"Edge endpoints must be between 1 and {n}: {e!r}")
        if int(u) == int(v):
            pytest.fail(f"Self-loop not allowed: {e!r}")
        a, b = sorted((int(u)-1, int(v)-1))
        edges.append((a, b))
    edges = sorted(set(edges))
    return edges


def _edges_to_adj(edges, n: int) -> np.ndarray:
    A = np.zeros((n, n), dtype=int)
    for u, v in edges:
        A[u, v] = 1
        A[v, u] = 1
    return A


def test_regular_and_neighborhood_property(construction, parameters):
    n = int(parameters.get("n", 0))
    d = int(parameters.get("d", 3))
    assert n > 0, "Incorrect. Parameter n must be a positive integer."
    try:
        edges = _parse_edge_list(construction, n)
        A = _edges_to_adj(edges, n)
    except Exception:
        A = _to_numeric_matrix(construction)
    assert A.ndim == 2 and A.shape[0] == A.shape[1], "Incorrect. Adjacency matrix must be square."
    assert A.shape[0] == n, f"Incorrect. Expected size {n}×{n}, got {A.shape[0]}×{A.shape[1]}."
    assert _is_zero_one_matrix(A), "Incorrect. Entries must be 0 or 1."
    assert _is_symmetric_zero_diag(A), "Incorrect. Matrix must be symmetric with zeros on the diagonal."
    deg = A.sum(axis=1)
    assert np.all(deg == d), (
        f"Incorrect. Not {d}-regular. Offending vertices (0-indexed): "
        f"{np.where(deg != d)[0].tolist()} with degrees {deg[np.where(deg != d)[0]].astype(int).tolist()}."
    )
    for i in range(n):
        Ni = np.where(A[i] == 1)[0].tolist()
        induced_edge_count = 0
        for a in range(d):
            for b in range(a + 1, d):
                u, v = Ni[a], Ni[b]
                induced_edge_count += int(A[u, v] == 1)
        assert induced_edge_count == 1, (
            f"Incorrect. For vertex {i}, neighbors {Ni} induce {induced_edge_count} edge(s); expected exactly 1."
        )
