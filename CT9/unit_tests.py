import json
import pytest


def _parse_construction(construction):
    """Accept a dict or a JSON string representing an object with keys 'n' and 'a'."""
    if isinstance(construction, dict):
        d = construction
    elif isinstance(construction, str):
        try:
            d = json.loads(construction)
        except Exception:
            pytest.fail("Submission must be a JSON object string or a dict.")
    else:
        pytest.fail("Unsupported construction type; submit a dict or JSON string.")

    if not isinstance(d, dict):
        pytest.fail("Submission must be a JSON object with keys 'n' and 'a'.")
    if 'n' not in d or 'a' not in d:
        pytest.fail("Missing 'n' or 'a' in submission.")

    n = d['n']
    a = d['a']

    if not isinstance(n, int):
        pytest.fail("n must be an integer.")
    if not (isinstance(a, list) and all(isinstance(x, int) for x in a)):
        pytest.fail("a must be a list of integers.")

    return n, list(a)


def _digits_in_base(n: int, base: int):
    if n < 0:
        raise ValueError("n must be nonnegative.")
    if base < 2:
        raise ValueError("base must be at least 2.")
    if n == 0:
        return [0]
    digits = []
    x = n
    while x > 0:
        digits.append(x % base)
        x //= base
    return list(reversed(digits))


def test_bases_and_palindromes(construction, parameters):
    m = int(parameters.get("m", 1))
    n, bases = _parse_construction(construction)
    assert len(bases) == m, f"Incorrect. Expected exactly m={m} bases, got {len(bases)}."
    assert all(b > 1 for b in bases), "Incorrect. All bases must be integers greater than 1."
    assert n > 0, "Incorrect. n must be a positive integer."
    for idx, b in enumerate(bases, start=1):
        digits = _digits_in_base(n, b)
        assert len(digits) == m, (
            f"Incorrect. In base a_{idx}={b}, n has {len(digits)} digits, but must have exactly m={m} digits."
        )
        assert digits == list(reversed(digits)), (
            f"Incorrect. In base a_{idx}={b}, the expansion is not a palindrome."
        )
