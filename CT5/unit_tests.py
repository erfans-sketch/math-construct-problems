import json
import ast
import pytest


def _normalize_subset(s, n):
    valid_types = (set, list, tuple, frozenset)
    if not isinstance(s, valid_types):
        raise ValueError("Each item must be a set/list/tuple of integers.")
    try:
        as_set = set(s)
    except Exception:
        raise ValueError("Each item must be convertible to a set of integers.")
    if len(as_set) == 0:
        raise ValueError("Subsets must be non-empty.")
    for x in as_set:
        if not isinstance(x, int):
            raise ValueError("Subset elements must be integers.")
        if x < 1 or x > n:
            raise ValueError(f"Subset elements must lie in 1..{n}.")
    return frozenset(as_set)


def _parse_construction(construction):
    if isinstance(construction, str):
        s = construction.strip()
        if s.startswith("```"):
            parts = s.split("\n", 1)
            if len(parts) == 2:
                s = parts[1]
            if s.endswith("```"):
                s = s.rsplit("\n", 1)[0] if "\n" in s else s[:-3]
        parsed = None
        try:
            parsed = json.loads(s)
        except Exception:
            try:
                parsed = ast.literal_eval(s)
            except Exception:
                pytest.fail("Unable to parse construction string. Submit a JSON array of arrays.")
        construction = parsed
    if isinstance(construction, tuple):
        construction = list(construction)
    if not isinstance(construction, list):
        pytest.fail("Construction must be a Python list of subsets.")
    return construction


def _check_intersections_in_circle(seq_sets):
    m = len(seq_sets)
    for i in range(m):
        a = seq_sets[i]
        b = seq_sets[(i + 1) % m]
        if len(a.intersection(b)) != 1:
            return False, f"Intersection condition fails between positions {i} and {(i+1)%m}."
    return True, "ok"


def test_length_and_uniqueness(construction, parameters):
    construction = _parse_construction(construction)
    n = int(parameters["n"]) 
    required_len = (1 << n) - 1
    assert len(construction) == required_len, (
        f"Incorrect length: expected {required_len}, got {len(construction)}."
    )
    normalized = [_normalize_subset(s, n) for s in construction]
    assert len(set(normalized)) == required_len, "There are duplicate subsets or invalid repetitions."


def test_elements_and_neighbor_intersection(construction, parameters):
    construction = _parse_construction(construction)
    n = int(parameters["n"]) 
    normalized = [_normalize_subset(s, n) for s in construction]
    ok, msg = _check_intersections_in_circle(normalized)
    assert ok, msg
