import json
import ast
from math import isqrt
from functools import reduce
from fractions import Fraction
import pytest


def _lcm(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    from math import gcd as _gcd
    return abs(a // _gcd(a, b) * b)

def _lcm_list(ints):
    return reduce(_lcm, ints, 1)

def _is_perfect_square(n: int) -> bool:
    if n < 0:
        return False
    r = isqrt(n)
    return r * r == n

def _normalize_construction(construction):
    if isinstance(construction, str):
        s = construction.strip()
        parsed = None
        try:
            parsed = json.loads(s)
        except Exception:
            try:
                parsed = ast.literal_eval(s)
            except Exception as e:
                pytest.fail(f"Unable to parse construction string: {e}")
        construction = parsed
    if isinstance(construction, dict) and "terms" in construction:
        terms = construction["terms"]
    else:
        terms = construction
    canon = []
    for t in terms:
        if isinstance(t, dict):
            a = int(t["a"]); b = int(t["b"]); num = int(t["num"]); den = int(t["den"])
        else:
            a, b, num, den = t
            a = int(a); b = int(b); num = int(num); den = int(den)
        if den == 0:
            pytest.fail("Denominator cannot be zero.")
        if den < 0:
            num, den = -num, -den
        canon.append({"a": a, "b": b, "num": num, "den": den})
    return canon

def _eval_P_exact(terms, x: int, y: int):
    L = _lcm_list([abs(t["den"]) for t in terms]) if terms else 1
    if L == 0:
        L = 1
    S = 0
    for t in terms:
        a, b, num, den = t["a"], t["b"], t["num"], t["den"]
        mon = pow(x, a) * pow(y, b)
        S += num * mon * (L // den)
    if S == 0:
        return (0, 1)
    from math import gcd as _gcd
    g = _gcd(abs(S), L)
    return (S // g, L // g)

def _reachable_values(terms, N: int, M: int):
    reached = set()
    for x in range(1, M):
        for y in range(1, M):
            num, den = _eval_P_exact(terms, x, y)
            if den != 1:
                continue
            v = num
            if 1 <= v < N:
                reached.add(v)
    return reached


def test_parameters_and_degree(construction, parameters):
    try:
        N = int(parameters["N"]) ; M = int(parameters["M"]) 
    except Exception as e:
        pytest.fail("Incorrect. parameters must include integers N and M.")
    assert N > 1 and M > 1, "Incorrect. Require N > 1 and M > 1."
    terms = _normalize_construction(construction)
    for t in terms:
        assert t["a"] >= 0 and t["b"] >= 0, "Incorrect. Exponents a,b must be non-negative integers."
        assert t["den"] != 0, "Incorrect. Denominator cannot be zero."
    coeffs = {}
    for t in terms:
        a, b, num, den = t["a"], t["b"], t["num"], t["den"]
        coeffs[(a, b)] = coeffs.get((a, b), Fraction(0)) + Fraction(num, den)
    nonzero_terms = [(a, b, c) for (a, b), c in coeffs.items() if c != 0]
    if nonzero_terms:
        max_deg = max(a + b for a, b, _ in nonzero_terms)
        assert max_deg < 5, f"Incorrect. Degree constraint violated: found degree {max_deg} ≥ 5."


def test_characterization_of_values(construction, parameters):
    N = int(parameters["N"]) ; M = int(parameters["M"]) 
    terms = _normalize_construction(construction)
    reached = _reachable_values(terms, N, M)
    for n in range(1, N):
        is_sq = _is_perfect_square(n)
        has = n in reached
        if has and is_sq:
            pytest.fail(f"Incorrect. n={n} is a perfect square but appears reachable.")
        if (not has) and (not is_sq):
            pytest.fail(f"Incorrect. Missing a non-square value n={n} under x,y < {M}.")
