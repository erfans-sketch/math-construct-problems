from __future__ import annotations
import math
import random
import numpy as np
from typing import Dict




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


def _is_prime(x: int) -> bool:
    if x < 2:
        return False
    if x % 2 == 0:
        return x == 2
    f = 3
    while f * f <= x:
        if x % f == 0:
            return False
        f += 2
    return True


def solution(parameters: Dict[str, int]) -> int:
    a = int(parameters.get("a", 1))
    # Guided search using n = 3m^2 with n + 1 composite, per the idea above.
    # Choose the smallest m such that n = 3m^2 > a.
    if a < 0:
        m_start = 1
    else:
        m_start = int(math.floor(math.sqrt(a / 3.0))) + 1

    max_steps = 20000  # adjustable search limit over m
    for step in range(max_steps):
        m = m_start + step
        n = 3 * m * m
        if n <= a:
            continue
        # Prefer cases where n + 1 is composite, as suggested by the approach
        if _is_prime(n + 1):
            continue

        # Optional: compute the two factors from the difference-of-squares view
        # f1 = n + 1 - 3m; f2 = n + 1 + 3m  # not strictly required for the check

        k = n ** 3 + 1
        if _divides_factorial(n, k):
            return n
