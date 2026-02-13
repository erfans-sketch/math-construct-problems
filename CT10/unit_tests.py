import numpy as np
import ast
import re
import pytest


def _parse_coeffs(construction):
    if isinstance(construction, (list, tuple, np.ndarray)):
        coeffs = list(construction)
        _ensure_int_list(coeffs)
        return coeffs
    if isinstance(construction, str):
        s = construction.strip()
        try:
            obj = ast.literal_eval(s)
            if isinstance(obj, (list, tuple, np.ndarray)):
                coeffs = list(obj)
                _ensure_int_list(coeffs)
                return coeffs
        except Exception:
            pass
        tokens = [t for t in re.split(r"[\,\s]+", s) if t]
        if not tokens:
            pytest.fail("Empty input.")
        try:
            coeffs = [int(t) for t in tokens]
        except Exception:
            pytest.fail("All coefficients must be integers.")
        return coeffs
    pytest.fail("Unsupported input type. Provide a list/tuple or a string.")


def _ensure_int_list(lst):
    for i, v in enumerate(lst):
        if isinstance(v, bool):
            pytest.fail("Booleans are not valid coefficients.")
        if isinstance(v, (int, np.integer)):
            continue
        if isinstance(v, float):
            if not float(v).is_integer():
                pytest.fail(f"Coefficient at index {i} is not an integer.")
            lst[i] = int(v)
        else:
            pytest.fail(f"Coefficient at index {i} is not an integer.")


def _eval_poly_at(coeffs, x):
    acc = 0
    for c in reversed(coeffs):
        acc = acc * x + int(c)
    return acc


def _is_power_of_two(v):
    if not isinstance(v, int):
        return False
    if v <= 0:
        return False
    return (v & (v - 1)) == 0


def test_poly_values_are_distinct_powers_of_two(construction, parameters):
    coeffs = _parse_coeffs(construction)
    assert len(coeffs) > 0, "Incorrect. Provide at least one coefficient."
    n = int(parameters.get("n", 1))
    assert n > 0, "Incorrect. Parameter n must be a positive integer."
    values = [_eval_poly_at(coeffs, k) for k in range(1, n + 1)]
    for idx, v in enumerate(values, start=1):
        assert _is_power_of_two(v), f"Incorrect. P({idx}) = {v} is not a positive power of 2."
    assert len(set(values)) == n, "Incorrect. The values P(1),...,P(n) are not all distinct."
