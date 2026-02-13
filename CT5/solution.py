from __future__ import annotations
from typing import List, Dict
import numpy as np
import random
import json
import ast



def _to_sorted_lists(seq: List[set]) -> List[List[int]]:
    return [sorted(list(s)) for s in seq]


def _lift_once(seq: List[set], new_elem: int) -> List[set]:
    """
    Apply the inductive step to transform a valid sequence for {1..new_elem-1}
    into a valid sequence for {1..new_elem}.
    `seq` is assumed to be a circular list [A1, A2, ..., Am] with m=2^n-1 and A1 singleton.
    Returns a new list of sets.
    """
    m = len(seq)
    assert m >= 1
    A = seq  # 0-based: A[0] corresponds to A1

    out: List[set] = []
    # Start with A1
    out.append(set(A[0]))

    # Descending block (m -> 2)
    for idx in range(m - 1, 0, -1):  # idx corresponds to Ai with i=idx+1
        i = idx + 1
        if i % 2 == 1:  # odd index -> plain
            out.append(set(A[idx]))
        else:  # even index -> lifted
            s = set(A[idx])
            s.add(new_elem)
            out.append(s)

    # Insert singleton {new_elem}
    out.append({new_elem})

    # Descending block again (m -> 2), complementary flavor
    for idx in range(m - 1, 0, -1):
        i = idx + 1
        if i % 2 == 1:  # odd index -> lifted
            s = set(A[idx])
            s.add(new_elem)
            out.append(s)
        else:  # even index -> plain
            out.append(set(A[idx]))

    # Close with A1 ∪ {new_elem}
    s = set(A[0])
    s.add(new_elem)
    out.append(s)

    return out


def _base_sequence_n3() -> List[set]:
    return [
        {1},
        {1, 2, 3},
        {2},
        {2, 3},
        {3},
        {1, 3},
        {1, 2},
    ]


def solution(parameters: Dict[str, int]) -> List[List[int]]:
    n = int(parameters.get("n", 6))
    if n < 3:
        raise ValueError("n must be at least 3 for this construction")

    # Build up from base n=3
    seq: List[set] = _base_sequence_n3()
    cur = 3
    while cur < n:
        seq = _lift_once(seq, cur + 1)
        cur += 1

    # Sanity: ensure sizes
    expected = (1 << n) - 1
    if len(seq) != expected:
        raise RuntimeError("Internal error: incorrect sequence length generated")

    return _to_sorted_lists(seq)