
import json
import ast
import math
import numpy as np
import pytest


def _as_int(x):
    if isinstance(x, bool):
        raise ValueError("Boolean is not a valid integer.")
    if isinstance(x, (int, np.integer)):
        return int(x)
    if isinstance(x, (float, np.floating)) and float(x).is_integer():
        return int(x)
    raise ValueError("Value is not an integer.")


def _flatten_two_numbers(container):
    if isinstance(container, (str, bytes)):
        s = container.decode("utf-8") if isinstance(container, (bytes,)) else container
        s = s.strip()
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
            container = parsed
    if isinstance(container, dict):
        if 'a' in container and 'b' in container:
            return _as_int(container['a']), _as_int(container['b'])
        if 'x' in container and 'y' in container:
            return _as_int(container['x']), _as_int(container['y'])
        raise ValueError("Dictionary must contain keys 'a' and 'b' (or 'x' and 'y').")

    if isinstance(container, np.ndarray):
        container = container.tolist()

    if isinstance(container, (int, float, np.integer, np.floating)):
        raise ValueError("Expected a 2-element container, got a scalar.")

    flat = []
    def _iter(obj):
        try:
            it = iter(obj)
        except TypeError:
            yield obj
            return
        for el in it:
            if isinstance(el, (list, tuple, np.ndarray)):
                for sub in _iter(el):
                    yield sub
            else:
                yield el
    for v in _iter(container):
        flat.append(v)
    flat = [x for x in flat if not isinstance(x, (str, bytes))]
    if len(flat) < 2:
        raise ValueError("Could not find two numeric entries for (a, b).")
    a = _as_int(flat[0])
    b = _as_int(flat[1])
    return a, b



def test_parse_two_integers(construction, parameters):
    """Verify that the submitted construction encodes two integers (a, b).

    This test succeeds when `_flatten_two_numbers` can extract two integer
    values from `construction`. It fails if parsing raises, if the values are
    missing, non-numeric, or not valid integers (e.g., booleans/floats that
    are not whole numbers).
    """
    try:
        a, b = _flatten_two_numbers(construction)
    except Exception:
        pytest.fail("Incorrect. Unable to parse (a, b) from the construction.")


def test_parameters_and_bounds(construction, parameters):
    """Validate presence/types of `n`, `m` and numeric bounds on a and b.

    Expects:
    - `parameters['n']` and `parameters['m']` exist and are integers
    - a > 0, b > 0
    - m > a > b > n
    Fails if any of these conditions are violated.
    """
    a, b = _flatten_two_numbers(construction)
    # Validate n
    try:
        n = int(parameters.get("n", None))
    except Exception:
        pytest.fail("Incorrect. Parameter 'n' must be an integer.")
    assert n is not None, "Incorrect. Missing parameter 'n'."
    # Validate m
    try:
        m = int(parameters.get("m", None))
    except Exception:
        pytest.fail("Incorrect. Parameter 'm' must be an integer.")
    assert m is not None, "Incorrect. Missing parameter 'm'."

    assert a > 0 and b > 0, "Incorrect. a and b must be positive integers."
    assert a > b, "Incorrect. a must be greater than b."
    assert a > n and b > n, f"Incorrect. Both a and b must be greater than n = {n}."
    assert a < m and b < m, f"Incorrect. Both a and b must be less than m = {m}."
    assert m > n, f"Incorrect. Expected m > n, got m = {m}, n = {n}."


def test_coprime(construction, parameters):
    """Ensure that a and b are coprime.

    The test fails when gcd(a, b) != 1, meaning a and b share a non-trivial
    common divisor.
    """
    a, b = _flatten_two_numbers(construction)
    assert math.gcd(a, b) == 1, "Incorrect. a and b are not coprime."


def _is_quadratic_residue_mod(k_mod: int, p: int) -> bool:
    """Return True if k_mod is a quadratic residue modulo odd prime p.
    We treat 0 as a residue. For p=2, everything is a residue.
    """
    if p == 2:
        return True
    if k_mod % p == 0:
        return True
    # Euler's criterion: a is QR mod p iff a^((p-1)/2) ≡ 1 (mod p)
    return pow(k_mod, (p - 1) // 2, p) == 1


def _is_perfect_square(k: int) -> bool:
    """Robust perfect-square test with fast modular pre-filtering.

    - For small-to-moderate k, use math.isqrt directly.
    - For large k, first run several small-prime quadratic-residue tests
      on k mod p. If any test fails, k is not a perfect square.
    - Only if it passes all modular tests compute math.isqrt(k).
    """
    if k < 0:
        return False
    # cheap exact checks for small numbers
    if k <= (1 << 60):  # reasonable threshold: direct isqrt cheap for <= 2^60
        r = int(math.isqrt(k))
        return r * r == k

    # Modular prefilter: if k is not a quadratic residue modulo any small prime p,
    # it cannot be a square. We compute k mod p without forming k by allowing
    # callers (when possible) to compute val modulo p — but here we accept k.
    # This loop uses a handful of small primes chosen to eliminate most nonsquares quickly.
    small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]
    for p in small_primes:
        if not _is_quadratic_residue_mod(k % p, p):
            return False

    # Passed modular tests — now do the definitive check
    r = int(math.isqrt(k))
    return r * r == k


def test_perfect_square_condition(construction, parameters):
    """Check that (a^2 + b) * (b^2 + a) is a perfect square.

    This test first uses modular quadratic-residue prefilters to avoid
    constructing and taking the square root of a massive intermediate when
    possible. Only if the modular filters pass do we compute the full value
    and confirm with math.isqrt.
    """
    a, b = _flatten_two_numbers(construction)

    # Quick bounds sanity for negative or zero (shouldn't happen due to other tests)
    if a < 0 or b < 0:
        pytest.fail("Incorrect. a and b must be non-negative for this test.")

    # Modular prefilter: compute the product modulo small primes using modular arithmetic
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    for p in small_primes:
        # compute (a^2 + b) * (b^2 + a) mod p without forming the big product
        a2pb_mod = (pow(a, 2, p) + (b % p)) % p
        b2pa_mod = (pow(b, 2, p) + (a % p)) % p
        val_mod = (a2pb_mod * b2pa_mod) % p
        # check quadratic residue modulo p
        if not _is_quadratic_residue_mod(val_mod, p):
            pytest.fail("Incorrect. (a^2 + b) * (b^2 + a) is not a perfect square.")

    # If it passed modular prefilters, do the exact big-int check once
    val = (a * a + b) * (b * b + a)
    if not _is_perfect_square(val):
        pytest.fail("Incorrect. (a^2 + b) * (b^2 + a) is not a perfect square.")
