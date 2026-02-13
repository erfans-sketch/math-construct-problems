from fractions import Fraction


def _add_poly(p, q):
    """Add two bivariate polynomials p and q.
    p, q: dict[(a,b)] -> Fraction coefficient for x^a y^b
    returns new dict
    """
    out = dict(p)
    for k, v in q.items():
        out[k] = out.get(k, Fraction(0)) + v
        if out[k] == 0:
            out.pop(k)
    return out


def _mul_poly(p, q):
    """Multiply two bivariate polynomials p and q.
    p, q: dict[(a,b)] -> Fraction
    returns new dict
    """
    out = {}
    for (a1, b1), c1 in p.items():
        for (a2, b2), c2 in q.items():
            k = (a1 + a2, b1 + b2)
            out[k] = out.get(k, Fraction(0)) + c1 * c2
            if out[k] == 0:
                out.pop(k)
    return out


def _scale_poly(p, s: Fraction):
    return {k: v * s for k, v in p.items() if v * s != 0}


def solution(parameters):
    """
    Construct P(x,y) = 1/4 * [ (x+y)^2 + 2(x-y) + 1 ]
    Return as a list of (a, b, num, den) tuples so that
    P(x,y) = sum (num/den) * x^a * y^b.
    """
    # Define x and y polynomials
    X = {(1, 0): Fraction(1)}
    Y = {(0, 1): Fraction(1)}

    # (x + y)
    X_plus_Y = _add_poly(X, Y)

    # (x + y)^2
    X_plus_Y_sq = _mul_poly(X_plus_Y, X_plus_Y)

    # 2(x - y)
    X_minus_Y = _add_poly(X, _scale_poly(Y, Fraction(-1)))
    two_X_minus_Y = _scale_poly(X_minus_Y, Fraction(2))

    # Constant 1
    ONE = {(0, 0): Fraction(1)}

    # Sum: (x+y)^2 + 2(x-y) + 1
    S = _add_poly(_add_poly(X_plus_Y_sq, two_X_minus_Y), ONE)

    # Scale by 1/4
    P = _scale_poly(S, Fraction(1, 4))

    # Convert to required list of tuples (a, b, num, den)
    # Sort for determinism by (a,b)
    terms = []
    for (a, b) in sorted(P.keys()):
        coeff = P[(a, b)]
        num = coeff.numerator
        den = coeff.denominator
        # Ensure positive denominator
        if den < 0:
            num, den = -num, -den
        terms.append((a, b, int(num), int(den)))

    return terms