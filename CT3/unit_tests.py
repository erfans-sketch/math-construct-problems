import json
import ast
import numpy as np
import pytest

EPS = 1e-9
DIR_TOL = 1e-3
OFF_TOL = 1e-3


def _as_points(construction):
    obj = construction
    if isinstance(obj, (str, bytes)):
        try:
            s = obj.decode("utf-8") if isinstance(obj, (bytes,)) else obj
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
                obj = parsed
        except Exception:
            pass
    try:
        arr = np.asarray(obj, dtype=float)
    except Exception:
        pytest.fail("Incorrect. Could not parse the construction as coordinates.")
    if arr.ndim != 2 or arr.shape[1] != 2:
        pytest.fail("Incorrect. Expected a list of n pairs [x, y].")
    if not np.all(np.isfinite(arr)):
        pytest.fail("Incorrect. Coordinates must be finite real numbers.")
    return arr


def _edge(p, q):
    v = q - p
    return v, float(np.hypot(v[0], v[1]))


def _area2(poly):
    x = poly[:, 0]
    y = poly[:, 1]
    return float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def _orient(a, b, c):
    return float((b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0]))


def _on_segment(a, b, c):
    return (min(a[0], b[0]) - EPS <= c[0] <= max(a[0], b[0]) + EPS and
            min(a[1], b[1]) - EPS <= c[1] <= max(a[1], b[1]) + EPS)


def _segments_intersect_strict(a, b, c, d):
    o1 = _orient(a, b, c)
    o2 = _orient(a, b, d)
    o3 = _orient(c, d, a)
    o4 = _orient(c, d, b)
    if (o1*o2 < -EPS) and (o3*o4 < -EPS):
        return True
    if abs(o1) <= EPS and _on_segment(a, b, c): return True
    if abs(o2) <= EPS and _on_segment(a, b, d): return True
    if abs(o3) <= EPS and _on_segment(c, d, a): return True
    if abs(o4) <= EPS and _on_segment(c, d, b): return True
    return False


def _canonical_line(p, q):
    d = q - p
    norm_d = float(np.hypot(d[0], d[1]))
    if norm_d <= EPS:
        return None
    a, b = -d[1] / norm_d, d[0] / norm_d
    if a < -DIR_TOL or (abs(a) <= DIR_TOL and b < -DIR_TOL):
        a, b = -a, -b
    c = a * p[0] + b * p[1]
    return (a, b, c)


def _same_line(L1, L2):
    a1, b1, c1 = L1
    a2, b2, c2 = L2
    if abs(a1 - a2) + abs(b1 - b2) > 5*DIR_TOL:
        return False
    return abs(c1 - c2) <= OFF_TOL


def _is_simple_polygon(poly):
    n = len(poly)
    if abs(_area2(poly)) <= EPS:
        return False, "Incorrect. Polygon area must be nonzero."
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        _, L = _edge(p, q)
        if L <= EPS:
            return False, f"Incorrect. Edge {i} has zero length."
    for i in range(n):
        a1, a2 = poly[i], poly[(i + 1) % n]
        for j in range(i + 1, n):
            b1, b2 = poly[j], poly[(j + 1) % n]
            if j == i or (j == (i + 1) % n) or (i == (j + 1) % n):
                continue
            if _segments_intersect_strict(a1, a2, b1, b2):
                return False, f"Incorrect. Edges {i} and {j} intersect."
    return True, "ok"


def _adjacent_edges_not_straight(poly):
    n = len(poly)
    for i in range(n):
        p0 = poly[i]
        p1 = poly[(i + 1) % n]
        p2 = poly[(i + 2) % n]
        v1, L1 = _edge(p0, p1)
        v2, L2 = _edge(p1, p2)
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        if L1 > EPS and L2 > EPS and abs(cross) <= DIR_TOL * L1 * L2 and dot < -DIR_TOL * L1 * L2:
            return False, (
                "Incorrect. The polygon must not have any 180° (straight) angles "
                f"at vertex {(i+1)%n}."
            )
    return True, "ok"


def test_vertex_count(construction, parameters):
    """Verify the polygon contains exactly `n` vertices from `parameters`.

    Fails if the provided construction does not decode to a 2D point array
    or if its vertex count differs from the required `n`.
    """
    n_param = parameters.get("n", None)
    poly = _as_points(construction)
    assert len(poly) == n_param, f"Incorrect. Expected {n_param} vertices, got {len(poly)}."


def test_polygon_simple_and_nonzero_area(construction, parameters):
    """Ensure the polygon is simple (no self-intersections) and has nonzero area.

    Also rejects zero-length edges and degenerate polygons. Uses geometric
    predicates with small tolerances to validate simplicity and area.
    """
    poly = _as_points(construction)
    ok, message = _is_simple_polygon(poly)
    assert ok, message


def test_no_straight_angles(construction, parameters):
    """Check that no interior angle is 180° (adjacent edges not collinear).

    Consecutive edges that are collinear and oppositely directed are flagged,
    ensuring every vertex induces a proper turn within tolerances.
    """
    poly = _as_points(construction)
    ok, message = _adjacent_edges_not_straight(poly)
    assert ok, message


def test_every_edge_has_collinear_partner(construction, parameters):
    """Require each edge to have another edge collinear with it (same line).

    For every boundary edge, constructs a canonical line representation and
    asserts there exists a distinct edge lying on the same line (within
    `DIR_TOL`/`OFF_TOL`). This encodes the "each side has a partner on its
    extension" constraint.
    """
    poly = _as_points(construction)
    n = len(poly)
    lines = []
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        L = _canonical_line(p, q)
        assert L is not None, f"Incorrect. Edge {i} is degenerate."
        lines.append(L)
    for i in range(n):
        has_partner = any(j != i and _same_line(lines[i], lines[j]) for j in range(n))
        assert has_partner, (
            "Incorrect. Each side must have another side lying on its extension "
            f"(edge {i} has no collinear partner)."
        )


