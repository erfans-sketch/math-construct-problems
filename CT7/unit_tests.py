import numpy as np
import pytest


def _parse_construction_str(construction):
    if isinstance(construction, str):
        s = construction.strip()
        if (s.startswith("[") and s.endswith("]")) or (s.startswith("(") and s.endswith(")")):
            s = s[1:-1].strip()
        if not s:
            return []
        try:
            return [int(part.strip()) for part in s.split(",")]
        except Exception as e:
            pytest.fail("Could not parse the comma-separated integer list.")
    return construction


def _is_permutation(seq, n):
    if not isinstance(seq, (list, tuple, np.ndarray)):
        return False, "Construction must be a list/tuple/array of integers."
    if len(seq) != n:
        return False, f"Incorrect length: expected {n}, got {len(seq)}."
    try:
        ints = [int(x) for x in seq]
    except Exception:
        return False, "All entries must be integers."
    if any(x < 1 or x > n for x in ints):
        return False, "Entries must be in the range 1..n."
    if len(set(ints)) != n:
        return False, "Entries must be distinct (a permutation of 1..n)."
    if any(x != y for x, y in zip(ints, seq)):
        for x in seq:
            if isinstance(x, (float, np.floating)) and not float(x).is_integer():
                return False, "All entries must be integers (no non-integer floats)."
    return True, None


def test_n_condition(construction, parameters):
    n = parameters.get('n')
    assert isinstance(n, int) and n > 0, "'n' must be a positive integer."
    assert n % 4 in (0, 1), f"n must satisfy n ≡ 0 or 1 (mod 4); got n = {n} (n % 4 = {n % 4})."


def test_permutation_and_diffs(construction, parameters):
    n = int(parameters['n'])
    construction = _parse_construction_str(construction)
    ok, msg = _is_permutation(construction, n)
    assert ok, msg
    a = [int(x) for x in construction]
    diffs = []
    for i, ai in enumerate(a, start=1):
        d = abs(ai - i)
        if d > 0:
            diffs.append(d)
    if len(set(diffs)) != len(diffs):
        seen = {}
        for i, ai in enumerate(a, start=1):
            d = abs(ai - i)
            if d == 0:
                continue
            if d in seen:
                j = seen[d]
                pytest.fail(
                    f"Positive differences are not distinct: |a_{j}-{j}| = |a_{i}-{i}| = {d}."
                )
            seen[d] = i
