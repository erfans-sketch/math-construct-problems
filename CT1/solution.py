import numpy as np
import ast
import json
import random
from typing import Dict, Tuple, List, Any

try:
    from scipy.sparse import coo_matrix, csr_matrix  # type: ignore
    _HAVE_SCIPY = True
except Exception:
    _HAVE_SCIPY = False
    

def build_adjacency_2k_gon_with_subdivided_fans(k: int, return_dense: bool = False):
    """
    Construct the graph as in the attached reference solution:
      - Start with a 2k-cycle on polygon vertices P_0..P_{2k-1}.
      - On each side {P_i, P_{i+1}} add an apex A_i.
      - Replace edges (A_i-P_i) and (A_i-P_{i+1}) by k parallel edges,
        then subdivide each by inserting (k-1) internal vertices, so each becomes a length-k path.

    Returns (A, info) where A is adjacency (dense np.ndarray if return_dense or no SciPy; else csr_matrix).
    """
    if k < 1:
        raise ValueError("k must be >= 1")

    n_poly = 2 * k
    n_apex = 2 * k
    n_subs = 4 * (k ** 2) * (k - 1) if k > 1 else 0

    N = n_poly + n_apex + n_subs

    base_poly = 0
    base_apex = n_poly
    base_subs = n_poly + n_apex

    edges: List[Tuple[int, int]] = []

    # Polygon cycle edges
    for i in range(n_poly):
        u = base_poly + i
        v = base_poly + ((i + 1) % n_poly)
        edges.append((min(u, v), max(u, v)))

    next_sub_idx = base_subs
    for i in range(n_poly):
        A_i = base_apex + i
        P_i = base_poly + i
        P_ip1 = base_poly + ((i + 1) % n_poly)
        for P in (P_i, P_ip1):
            for _p in range(k):
                if k == 1:
                    u, v = sorted((A_i, P))
                    edges.append((u, v))
                else:
                    internal = list(range(next_sub_idx, next_sub_idx + (k - 1)))
                    next_sub_idx += (k - 1)
                    prev = A_i
                    for vtx in internal:
                        u_, v_ = sorted((prev, vtx))
                        edges.append((u_, v_))
                        prev = vtx
                    u_, v_ = sorted((prev, P))
                    edges.append((u_, v_))

    assert next_sub_idx == N, f"Indexing mismatch: used {next_sub_idx} but N={N}"

    # Build adjacency
    if (_HAVE_SCIPY and not return_dense):
        rows = [u for (u, v) in edges] + [v for (u, v) in edges]
        cols = [v for (u, v) in edges] + [u for (u, v) in edges]
        data = np.ones(len(rows), dtype=np.int8)
        A = coo_matrix((data, (rows, cols)), shape=(N, N)).tocsr()
    else:
        A = np.zeros((N, N), dtype=np.int8)
        for (u, v) in edges:
            A[u, v] = 1
            A[v, u] = 1

    info: Dict[str, Any] = {
        'poly': (base_poly, base_poly + n_poly),
        'apex': (base_apex, base_apex + n_apex),
        'subs': (base_subs, base_subs + n_subs),
        'n_vertices': N,
        'n_edges': len(edges),
        'k': k,
    }
    return A, info


def construct_graph(k: int) -> List[List[int]]:
    """
    Return a 0/1 adjacency matrix (list of lists) for k > 1.
    Ensures: every edge lies on a 2k-cycle and a (2k+1)-cycle, and no cycle has length divisible by 2k-1.
    """
    if k <= 1:
        raise ValueError("k must be > 1")
    A, _info = build_adjacency_2k_gon_with_subdivided_fans(k, return_dense=True)
    return A.astype(int).tolist()

def solution(parameters):
    k = parameters["even_cycle"]//2
    return construct_graph(k)