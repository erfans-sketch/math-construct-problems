import ast
import pytest

DIR_ORDER = ['E', 'S', 'W', 'N']


def _parse_path(construction):
    if isinstance(construction, str):
        s = construction.strip()
        try:
            obj = ast.literal_eval(s)
        except Exception as e:
            pytest.fail("Could not parse string as Python literal")
    else:
        obj = construction
    if not isinstance(obj, (list, tuple)):
        pytest.fail("Path must be a list/tuple of [x,y] points")
    path = []
    for p in obj:
        if not isinstance(p, (list, tuple)) or len(p) != 2:
            pytest.fail("Each vertex must be a list/tuple of length 2")
        x, y = p
        try:
            xi = int(x); yi = int(y)
        except Exception:
            pytest.fail("Coordinates must be integers")
        path.append((xi, yi))
    if len(path) < 2:
        pytest.fail("Path must contain at least two points")
    return path


def _build_town_graph(n):
    allowed_edges = set()
    edge_dir = {}
    def add_edge(u, v):
        if u == v:
            return
        dx = v[0] - u[0]; dy = v[1] - u[1]
        if   (dx, dy) == (1, 0): d = 'E'
        elif (dx, dy) == (-1, 0): d = 'W'
        elif (dx, dy) == (0, 1): d = 'N'
        elif (dx, dy) == (0, -1): d = 'S'
        else:
            return
        allowed_edges.add((u, v))
        edge_dir[(u, v)] = d
    for y in range(0, n + 1):
        for x in range(0, n):
            a = (x, y); b = (x + 1, y)
            if y == 0:
                add_edge(b, a)
            elif y == n:
                add_edge(a, b)
            else:
                add_edge(a, b); add_edge(b, a)
    for x in range(0, n + 1):
        for y in range(0, n):
            a = (x, y); b = (x, y + 1)
            if x == 0:
                add_edge(a, b)
            elif x == n:
                add_edge(b, a)
            else:
                add_edge(a, b); add_edge(b, a)
    expected_edge_count = 4 * (n ** 2)
    return allowed_edges, edge_dir, expected_edge_count


def _right_turn_or_straight(prev_dir, new_dir):
    if prev_dir is None:
        return True
    i = DIR_ORDER.index(prev_dir)
    straight = prev_dir
    right = DIR_ORDER[(i + 1) % 4]
    return new_dir == straight or new_dir == right


def _expand_turning_points(turns, n):
    if len(turns) < 2:
        pytest.fail("At least two turning points are required")
    full = [turns[0]]
    for i in range(len(turns) - 1):
        (x1, y1) = turns[i]; (x2, y2) = turns[i + 1]
        dx = x2 - x1; dy = y2 - y1
        if dx != 0 and dy != 0:
            pytest.fail("Points are not axis-aligned (no diagonals allowed).")
        if dx == 0 and dy == 0:
            pytest.fail("Zero-length segment in turning points list")
        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
        steps = abs(dx) + abs(dy)
        for _ in range(steps):
            px, py = full[-1]
            nx, ny = px + step_x, py + step_y
            full.append((nx, ny))
    return full


def _assert_compressed_turns(turns):
    """
    Enforce: "Intermediate intersections on straight segments must be omitted."
    That means the provided list must only contain actual turning points
    (plus start/end). Therefore, consecutive segments must alternate axis:
    ... horizontal, vertical, horizontal, ... (or vice versa).
    """
    if len(turns) < 2:
        pytest.fail("At least two turning points are required")

    def seg_axis(a, b):
        (x1, y1), (x2, y2) = a, b
        dx, dy = x2 - x1, y2 - y1
        if dx != 0 and dy != 0:
            pytest.fail("Points are not axis-aligned (no diagonals allowed).")
        if dx == 0 and dy == 0:
            pytest.fail("Zero-length segment in turning points list")
        return 'H' if dy == 0 else 'V'

    # Require alternating axes. If two adjacent segments share the same axis,
    # then the middle point is an unnecessary intermediate on a straight segment.
    for i in range(1, len(turns) - 1):
        a, b, c = turns[i - 1], turns[i], turns[i + 1]
        axis1 = seg_axis(a, b)
        axis2 = seg_axis(b, c)
        assert axis1 != axis2, (
            "Incorrect. Intermediate intersections on straight segments must be omitted; "
            f"remove redundant point {b} between {a} and {c}."
        )


def test_route_uses_all_directed_sides_once(construction, parameters):
    """
    Validate that a proposed route over an (n+1) x (n+1) grid-town uses every
    directed street side exactly once while only going straight or turning right.

    High-level logic:
    1) Parse and normalize the provided "construction" into a list of integer
        turning points on the grid; enforce that the list is compressed, i.e.,
        no intermediate points on straight segments.
    2) Build the directed grid graph according to the town rules:
        - Interior edges are bidirectional.
        - On the outer boundary, directions follow the problem statement.
        This yields the allowed directed edges, a map from edge->direction, and
        the expected total number of directed sides (4 * n^2).
    3) Expand the compressed turning points into the full step-by-step path,
        moving one grid unit at a time.
    4) Simulate traversal:
        - Each consecutive pair must be neighboring grid points and belong to
        the allowed directed edges.
        - Count usage of each directed edge and ensure it is used exactly once.
        - Track the compass directions to enforce only straight or right turns.
    5) At the end, assert that the number of used directed edges equals the
        expected 4 * n^2 and that no directed edge remains unused.

    parameters:
    - construction: str | list[tuple[int,int]] | list[list[int]]
    The user-provided turning points, possibly as a string literal.
    - parameters: dict with key 'n' specifying the grid size.
    """
    n = parameters["n"]
    turns = _parse_path(construction)
    # Enforce compression of the provided turning points list.
    _assert_compressed_turns(turns)
    for (x, y) in turns:
        assert 0 <= x <= n and 0 <= y <= n, (
            f"Incorrect. Point {(x, y)} lies outside the town grid [0,{n}]x[0,{n}]."
        )
    allowed_edges, edge_dir, expected_edge_count = _build_town_graph(n)
    path = _expand_turning_points(turns, n)
    edge_usage = {e: 0 for e in allowed_edges}
    dirs_in_path = []
    for i in range(len(path) - 1):
        u = path[i]; v = path[i + 1]
        dx = v[0] - u[0]; dy = v[1] - u[1]
        assert abs(dx) + abs(dy) == 1, (
            f"Incorrect. Consecutive points {u} -> {v} are not neighbors."
        )
        assert (u, v) in allowed_edges, (
            f"Incorrect. Move {u} -> {v} is not along an allowed street segment."
        )
        edge_usage[(u, v)] += 1
        assert edge_usage[(u, v)] == 1, f"Incorrect. Street side {u} -> {v} is used more than once."
        dirs_in_path.append(edge_dir[(u, v)])
    for i in range(1, len(dirs_in_path)):
        prev_d = dirs_in_path[i - 1]
        new_d = dirs_in_path[i]
        assert _right_turn_or_straight(prev_d, new_d), (
            "Incorrect. Only straight or right turns are allowed."
        )
    used_edges_count = sum(edge_usage.values())
    assert used_edges_count == expected_edge_count, (
        f"Incorrect. The route traverses {used_edges_count} directed street sides, "
        f"but there are exactly {expected_edge_count} such sides in the town."
    )
    missing = [e for e, cnt in edge_usage.items() if cnt == 0]
    assert not missing, (
        f"Incorrect. The route does not use all street sides exactly once; example missing side: {missing[0]}."
    )
