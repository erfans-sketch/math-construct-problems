import math
import pytest


def _clean_int(x):
    if isinstance(x, bool):
        raise ValueError("Boolean not allowed for n")
    if isinstance(x, int):
        return x
    if isinstance(x, float):
        if abs(x - int(round(x))) < 1e-9:
            return int(round(x))
        raise ValueError("Non-integer float provided for n.")
    if isinstance(x, str):
        s = x.strip()
        if s.startswith('+'):
            s = s[1:]
        return int(s)
    raise TypeError("Construction must be an integer or numeric string.")


def _prime_factors_with_exponents(m: int):
    if m <= 0:
        raise ValueError("m must be positive")
    x = m
    pf = {}
    while x % 2 == 0:
        pf[2] = pf.get(2, 0) + 1
        x //= 2
    f = 3
    while f * f <= x:
        while x % f == 0:
            pf[f] = pf.get(f, 0) + 1
            x //= f
        f += 2
    if x > 1:
        pf[x] = pf.get(x, 0) + 1
    return pf


def _vp_factorial(n: int, p: int) -> int:
    if p < 2:
        return 0
    e = 0
    nn = n
    while nn:
        nn //= p
        e += nn
    return e


def _divides_factorial(n: int, k: int) -> bool:
    if k <= 0:
        return False
    pf = _prime_factors_with_exponents(k)
    for p, e in pf.items():
        if _vp_factorial(n, p) < e:
            return False
    return True


def test_n_is_integer(construction, parameters):
    try:
        _ = _clean_int(construction)
    except Exception:
        pytest.fail("Invalid input for n")


def test_bounds_and_divisibility(construction, parameters):
    n = _clean_int(construction)
    a = parameters.get("a", None)
    b = parameters.get("b", None)
    assert a is not None, "Internal error: parameter 'a' missing."
    assert b is not None, "Internal error: parameter 'b' missing."
    assert n > 0, "n must be a positive integer."
    assert n > a, f"n must be strictly greater than a={a}."
    assert n < b, f"n must be strictly less than b={b}."
    k = n**3 + 1
    assert _divides_factorial(n, k), "Incorrect: (n^3 + 1) does not divide n!."
