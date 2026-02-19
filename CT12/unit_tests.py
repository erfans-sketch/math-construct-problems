import numpy as np
import ast
import pytest


def _to_int(x):
    if isinstance(x, (int, np.integer)):
        return int(x)
    if isinstance(x, (float, np.floating)) and float(x).is_integer():
        return int(x)
    if isinstance(x, str):
        return int(x.strip())
    raise ValueError("n must be an integer")


def _extract_n(construction):
    if isinstance(construction, dict) and 'n' in construction:
        return _to_int(construction['n'])
    if isinstance(construction, (int, np.integer)):
        return int(construction)
    if isinstance(construction, (float, np.floating)):
        if float(construction).is_integer():
            return int(construction)
        raise ValueError("n must be an integer")
    if isinstance(construction, str):
        s = construction.strip()
        try:
            obj = ast.literal_eval(s)
            return _extract_n(obj)
        except Exception:
            return int(s)
    raise ValueError("Could not extract an integer n from the submission")


def _is_sum_of_two_squares(N: int) -> bool:
    if N < 0:
        return False
    if N in (0, 1):
        return True
    n = N
    while n % 2 == 0:
        n //= 2
    p = 3
    while p * p <= n:
        exp = 0
        while n % p == 0:
            n //= p
            exp += 1
        if exp % 2 == 1 and (p % 4) == 3:
            return False
        p += 2
    if n > 1 and (n % 4) == 3:
        return False
    return True


def test_n_and_condition(construction, parameters):
    try:
        n = _extract_n(construction)
    except Exception as e:
        pytest.fail(f"Incorrect. Could not parse n: {e}")
    M = parameters.get("M", 1)
    assert isinstance(M, int) and M > 0, "Internal checker error: parameter M must be a positive integer"
    assert n > M, f"Incorrect. Your n={n} is not greater than M={M}."
    N = n**3 - 2
    assert N > 0, f"Incorrect. n^3 - 2 must be positive; got {N}."
    assert _is_sum_of_two_squares(N), (
        f"Incorrect. n={n} does not work since n^3 - 2 = {N} is not a sum of two squares."
    )
