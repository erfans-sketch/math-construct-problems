"""
Construct a polynomial P with integer coefficients such that
P(1), P(2), ..., P(n) are distinct powers of 2.

Construction idea (product trick):
- Let g(x) = ∏_{r=1}^n (x - r). For each i, define h_i(x) = g(x)/(x - i),
  which has integer coefficients.
- Let s_i = h_i(i) = ∏_{r\ne i} (i - r) = (i-1)! * (-1)^{n-i} * (n-i)!.
- Choose exponents a_i so that a_i >= v2(s_i) and the set {a_i} is distinct.
  We take a_i = M + 2^i where M = max_i v2(s_i).
- Using Euler's theorem on the odd part of s_i, pick T_i = a_i + L_i where
  L_i is a multiple of φ(odd_part(s_i)) so that s_i | (2^{T_i} - 2^{a_i}).
  Then k_i = (2^{T_i} - 2^{a_i}) // s_i is an integer and
  f_i(x) = 2^{a_i} + k_i * h_i(x) satisfies:
    f_i(j) = 2^{a_i} for j \ne i, and f_i(i) = 2^{T_i}.
- Finally set P(x) = ∏_{i=1}^n f_i(x). Then, for each j,
    P(j) = 2^{ (∑_{i\ne j} a_i) + T_j },
  which is a power of two. Distinctness follows since the exponents differ
  (the set {a_i} is distinct; even if T_j are equal across j, the missing a_j
  changes the sum).

Return coefficients in increasing degree order as a list of Python ints.
"""
from math import factorial
import math


def _poly_mul(a, b):
    """Multiply two polynomials given in increasing degree order."""
    res = [0] * (len(a) + len(b) - 1)
    for i, av in enumerate(a):
        if av == 0:
            continue
        for j, bv in enumerate(b):
            if bv == 0:
                continue
            res[i + j] += av * bv
    return res


def _poly_add(a, b):
    """Add two polynomials in increasing degree order."""
    m = max(len(a), len(b))
    out = [0] * m
    for i in range(m):
        av = a[i] if i < len(a) else 0
        bv = b[i] if i < len(b) else 0
        out[i] = av + bv
    return out


def _poly_from_linear(term_root):
    """Return coefficients of (x - term_root) in increasing degree order."""
    return [-term_root, 1]


def _build_g(n):
    p = [1]
    for r in range(1, n + 1):
        p = _poly_mul(p, _poly_from_linear(r))
    return p  # degree n, inc order


def _synthetic_div_by_x_minus(p_inc, a):
    """Divide polynomial (inc order) by (x - a), return quotient (inc order).
    Assumes exact division (here true for g(x)).
    """
    # Convert to desc order for standard synthetic division
    p_desc = list(reversed(p_inc))  # a_n, a_{n-1}, ..., a_0
    n = len(p_desc) - 1  # degree
    q_desc = [0] * n
    q_desc[0] = p_desc[0]
    for k in range(1, n):
        q_desc[k] = p_desc[k] + a * q_desc[k - 1]
    # remainder would be p_desc[-1] + a * q_desc[-1]
    q_inc = list(reversed(q_desc))
    return q_inc


def _eval_poly_inc(coeffs, x):
    acc = 0
    for c in reversed(coeffs):
        acc = acc * x + int(c)
    return acc


def _v2(m):
    """2-adic valuation v2(m): highest e such that 2^e divides m (m != 0)."""
    m = abs(int(m))
    if m == 0:
        return 0
    e = 0
    while (m & 1) == 0:
        m >>= 1
        e += 1
    return e


def _phi(m):
    """Euler's totient function for m >= 1."""
    m = int(m)
    if m <= 1:
        return 1
    result = m
    d = 2
    x = m
    while d * d <= x:
        if x % d == 0:
            while x % d == 0:
                x //= d
            result -= result // d
        d += 1
    if x > 1:
        result -= result // x
    return result

def _lcm(a: int, b: int) -> int:
    return abs(a // math.gcd(a, b) * b) if a and b else 0


def solution(parameters):
    n = int(parameters.get("n") or parameters.get("m") or 5)
    if n <= 0:
        return [1]

    # G(x) = ∏_{r=1}^n (x - r)
    G = _build_g(n)

    # Precompute s_i, a_i=v2(s_i), odd parts and φ(odd part), and g_i(x)
    s_vals = []
    a_vals = []
    phi_vals = []
    g_list = []
    for i in range(1, n + 1):
        sign = -1 if ((n - i) % 2 == 1) else 1
        s_i = sign * factorial(i - 1) * factorial(n - i)
        a_i = _v2(s_i)
        odd_i = abs(s_i) >> a_i  # odd part (≥1)
        phi_i = _phi(odd_i)

        s_vals.append(s_i)
        a_vals.append(a_i)
        phi_vals.append(phi_i)
        g_list.append(_synthetic_div_by_x_minus(G, i))

    # Choose L = lcm_i φ(odd_i), then set T_i = a_i + L * i to make exponents distinct
    L = 1
    for phi in phi_vals:
        L = _lcm(L, phi)
    if L == 0:
        L = 1

    # Build f_i(x) = 2^{a_i} + k_i * g_i(x), where k_i = (2^{T_i} - 2^{a_i}) / s_i
    f_list = []
    for idx in range(n):
        a_i = a_vals[idx]
        s_i = s_vals[idx]
        g_i = g_list[idx]
        T_i = a_i + L * (idx + 1)  # ensure distinct exponents at points 1..n
        num = (1 << T_i) - (1 << a_i)
        k_i = num // s_i  # guaranteed integer by construction

        # f_i coefficients in increasing order
        fi = [k_i * c for c in g_i]
        if fi:
            fi[0] += (1 << a_i)
        else:
            fi = [(1 << a_i)]
        f_list.append(fi)

    # P(x) = ∏ f_i(x)
    P = [1]
    for fi in f_list:
        P = _poly_mul(P, fi)

    while len(P) > 1 and P[-1] == 0:
        P.pop()
    return [int(c) for c in P]
