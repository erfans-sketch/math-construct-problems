import json
import ast
import pytest


def orient(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])

def on_segment(a, b, p):
    if min(a[0], b[0]) - 1e-9 <= p[0] <= max(a[0], b[0]) + 1e-9 and \
       min(a[1], b[1]) - 1e-9 <= p[1] <= max(a[1], b[1]) + 1e-9:
        return abs(orient(a, b, p)) <= 1e-9
    return False

def segments_intersect(p1, p2, q1, q2):
    o1 = orient(p1, p2, q1)
    o2 = orient(p1, p2, q2)
    o3 = orient(q1, q2, p1)
    o4 = orient(q1, q2, p2)
    if (o1 == 0 and on_segment(p1, p2, q1)) or \
       (o2 == 0 and on_segment(p1, p2, q2)) or \
       (o3 == 0 and on_segment(q1, q2, p1)) or \
       (o4 == 0 and on_segment(q1, q2, p2)):
        return True
    return (o1 > 0 and o2 < 0 or o1 < 0 and o2 > 0) and \
           (o3 > 0 and o4 < 0 or o3 < 0 and o4 > 0)

def is_simple_polygon(poly):
    n = len(poly)
    if n < 3:
        return False, "Polygon must have at least 3 vertices."
    for i in range(n):
        a1 = poly[i]; a2 = poly[(i+1) % n]
        for j in range(i+1, n):
            if (j == i+1) or ((i == 0) and (j == n-1)):
                continue
            b1 = poly[j]; b2 = poly[(j+1) % n]
            if segments_intersect(a1, a2, b1, b2):
                return False, f"Edges {(i, i+1)} and {(j, (j+1) % n)} intersect."
    return True, "Simple polygon."

def point_in_polygon(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i+1)%n]
        if on_segment((x1,y1),(x2,y2),(x,y)):
            return True
        if ((y1 > y) != (y2 > y)):
            x_int = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x_int == x:
                return True
            if x_int > x:
                inside = not inside
    return inside

def is_valid_diagonal(i, j, poly):
    n = len(poly)
    if i == j:
        return False
    if (i+1) % n == j or (j+1) % n == i:
        return False
    a = poly[i]; b = poly[j]
    for k in range(n):
        k2 = (k+1) % n
        if k == i or k == j or k2 == i or k2 == j:
            continue
        c = poly[k]; d = poly[k2]
        if segments_intersect(a, b, c, d):
            return False
    mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
    if not point_in_polygon(mid, poly):
        return False
    return True

def count_triangulations(poly):
    n = len(poly)
    if n < 3:
        return 0
    valid = [[False]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if (i+1) % n == j or (j+1) % n == i:
                valid[i][j] = True
            else:
                valid[i][j] = is_valid_diagonal(i, j, poly)
    dp = [[0]*n for _ in range(n)]
    for i in range(n-1):
        dp[i][i+1] = 1
    for length in range(2, n):
        for i in range(0, n - length):
            j = i + length
            if not valid[i][j]:
                dp[i][j] = 0
                continue
            total = 0
            for k in range(i+1, j):
                if not valid[i][k] or not valid[k][j]:
                    continue
                total += dp[i][k] * dp[k][j]
            dp[i][j] = total
    return dp[0][n-1]

def _parse_construction_points(construction):
    parsed = construction
    if isinstance(construction, str):
        text = construction.strip()
        try:
            parsed = json.loads(text)
        except Exception:
            try:
                parsed = ast.literal_eval(text)
            except Exception as e:
                pytest.fail("Invalid construction text. Provide a JSON/Python list of coordinate pairs.")
    if isinstance(parsed, (list, tuple)) and len(parsed) == 1 and isinstance(parsed[0], (list, tuple)) and parsed and parsed[0]:
        if isinstance(parsed[0][0], (list, tuple)) and len(parsed[0][0]) == 2:
            parsed = parsed[0]
    try:
        if not isinstance(parsed, (list, tuple)):
            raise TypeError("Top-level object is not a list of points")
        poly = []
        for i, v in enumerate(parsed):
            if not isinstance(v, (list, tuple)) or len(v) != 2:
                raise ValueError(f"Point at index {i} is not a pair: {v}")
            x, y = v
            poly.append((float(x), float(y)))
    except Exception as e:
        pytest.fail("Invalid construction format. Expect list of [x,y] pairs.")
    return poly


def test_simple_polygon_and_triangulations(construction, parameters):
    poly = _parse_construction_points(construction)
    assert len(poly) >= 3, "Invalid polygon: fewer than 3 vertices."
    for i in range(len(poly)):
        a = poly[i]; b = poly[(i+1) % len(poly)]
        assert not (abs(a[0]-b[0]) < 1e-12 and abs(a[1]-b[1]) < 1e-12), (
            f"Invalid polygon: consecutive vertices {i} and {(i+1)%len(poly)} are identical."
        )
    ok, msg = is_simple_polygon(poly)
    assert ok, f"Polygon not simple: {msg}"
    try:
        num = count_triangulations(poly)
    except Exception as e:
        pytest.fail(f"Error counting triangulations: {e}")
    target = parameters.get("n", None)
    assert target is not None, "Parameter 'n' not provided."
    assert num == target, f"Incorrect: polygon has {num} triangulation(s); expected {target}."
