import json
import ast
import pytest


def _segments_intersect(p1, p2, q1, q2):
    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])
    return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)


def _parse_construction_indices(construction):
    parsed = construction
    if isinstance(construction, str):
        text = construction.strip()
        try:
            parsed = json.loads(text)
        except Exception:
            try:
                parsed = ast.literal_eval(text)
            except Exception:
                if "," in text:
                    parsed = [int(t.strip()) for t in text.split(",") if t.strip() != ""]
                else:
                    pytest.fail("Invalid construction. Provide a list of indices, e.g. [1,2,3] or '1,2,3'.")
    if not isinstance(parsed, (list, tuple)):
        pytest.fail("Top-level must be a list of indices")
    out = []
    for v in parsed:
        out.append(int(v))
    return out


def test_simple_polygon_from_indices(construction, parameters):
    n = parameters["n"]
    points = parameters["point_positions"]
    indices = _parse_construction_indices(construction)
    norm_points = {int(k): v for k, v in points.items()}
    assert len(indices) == n, f"Incorrect. Polygon must have {n} vertices"
    assert set(indices) == set(norm_points.keys()), "Incorrect. Polygon must use all given points exactly once"
    try:
        edges = [(norm_points[indices[i]], norm_points[indices[(i + 1) % n]]) for i in range(n)]
    except Exception:
        pytest.fail("Incorrect. An index in the construction is not in point_positions")
    for i, (p1, p2) in enumerate(edges):
        for j, (q1, q2) in enumerate(edges):
            if abs(i - j) in (0, 1, n - 1):
                continue
            assert not _segments_intersect(p1, p2, q1, q2), f"Incorrect. Edges {i+1} and {j+1} intersect"
