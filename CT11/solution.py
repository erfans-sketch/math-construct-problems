from typing import List, Tuple, Set

# Directions in clockwise order for right turns
DIR_ORDER = ["E", "S", "W", "N"]
DIR_DELTA = {
    "E": (1, 0),
    "S": (0, -1),
    "W": (-1, 0),
    "N": (0, 1),
}


def _right(d: str) -> str:
    i = DIR_ORDER.index(d)
    return DIR_ORDER[(i + 1) % 4]


def _is_boundary(x: int, y: int, n: int) -> bool:
    return x == 0 or x == n or y == 0 or y == n


def _build_marks(n: int) -> Set[Tuple[int, int]]:
    """
    Construct the set of marked interior intersections (turn-right posters)
    according to the constructive pattern described in the solution.

    Patterns by n mod 3:
    - n = 3k + 2 (n >= 2): (2,1), (3,3), (5,4), (6,6), ... up to within (n-2, n-2)
    - n = 3k + 1 (n >= 4): (2,1), (1,2), (4,3), (5,5), (7,6), ... up to within (n-2, n-2)
    - n = 3k     (n >= 6): (2,1), (1,2), (3,2), (4,4), (6,5), (7,7), ... up to within (n-2, n-2)

    We always keep points strictly inside: 1 <= x,y <= n-1. We stop before exceeding n-2.
    """
    marks: Set[Tuple[int, int]] = set()
    t = n - 2
    if t < 1:
        return marks

    rem = n % 3

    def add_point(p: Tuple[int, int]):
        x, y = p
        if 1 <= x <= t and 1 <= y <= t:
            marks.add((x, y))

    # Alternating small diagonal-forward steps used after seeding
    alternates = [(1, 2), (2, 1)]

    if rem == 2:
        # Start at (2,1) then alternate +1,+2 and +2,+1
        pos = (2, 1)
        add_point(pos)
        idx = 0
        while True:
            nx = pos[0] + alternates[idx][0]
            ny = pos[1] + alternates[idx][1]
            if nx > t or ny > t:
                break
            pos = (nx, ny)
            add_point(pos)
            idx ^= 1

    elif rem == 1:
        # Seed: (2,1), (1,2), (4,3); then alternate starting with +1,+2
        pos = None
        for s in [(2, 1), (1, 2), (4, 3)]:
            if s[0] <= t and s[1] <= t:
                add_point(s)
                pos = s
        if pos == (4, 3):
            idx = 0  # next +1,+2, then +2,+1...
            while True:
                nx = pos[0] + alternates[idx][0]
                ny = pos[1] + alternates[idx][1]
                if nx > t or ny > t:
                    break
                pos = (nx, ny)
                add_point(pos)
                idx ^= 1
        # If pos is (1,2) or (2,1) only, we're done; nothing further fits within bounds.

    else:  # rem == 0
        # Seed: (2,1), (1,2), (3,2), (4,4); then alternate starting with +2,+1
        pos = None
        for s in [(2, 1), (1, 2), (3, 2), (4, 4)]:
            if s[0] <= t and s[1] <= t:
                add_point(s)
                pos = s
        if pos == (4, 4):
            idx = 1  # next +2,+1, then +1,+2...
            while True:
                nx = pos[0] + alternates[idx][0]
                ny = pos[1] + alternates[idx][1]
                if nx > t or ny > t:
                    break
                pos = (nx, ny)
                add_point(pos)
                idx ^= 1
        # If pos is earlier in the seed list, no more points fit; stop.

    return marks


def _next_dir(x: int, y: int, prev_dir: str, marks: Set[Tuple[int, int]], n: int) -> str:
    # Always turn right on boundary; inside, turn right iff marked, else go straight
    if _is_boundary(x, y, n):
        return _right(prev_dir)
    if (x, y) in marks:
        return _right(prev_dir)
    return prev_dir


def _expected_edge_count(n: int) -> int:
    # Matches CT11_verify: 4 * n^2 directed street sides
    return 4 * (n ** 2)


def _dir_of(u: Tuple[int, int], v: Tuple[int, int]) -> str:
    dx = v[0] - u[0]
    dy = v[1] - u[1]
    if (dx, dy) == (1, 0):
        return "E"
    if (dx, dy) == (-1, 0):
        return "W"
    if (dx, dy) == (0, 1):
        return "N"
    if (dx, dy) == (0, -1):
        return "S"
    raise ValueError("Non-adjacent vertices in path construction")


def _traverse_full_cycle(n: int, marks: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Build the unique big cycle induced by the deterministic local rule (straight
    vs. right at marked/boundary intersections) as a sequence of vertices.

    We start from the boundary edge (n,0) -> (n-1,0) and follow the induced
    successor mapping on directed edges until the start edge is reached again.
    """
    start_u = (n, 0)
    start_v = (n - 1, 0)
    start_edge = (start_u, start_v)

    path: List[Tuple[int, int]] = [start_u, start_v]
    visited_edges: Set[Tuple[Tuple[int, int], Tuple[int, int]]] = {start_edge}

    u, v = start_edge
    prev_dir = _dir_of(u, v)

    expected = _expected_edge_count(n)

    while True:
        x, y = v
        nd = _next_dir(x, y, prev_dir, marks, n)
        dx, dy = DIR_DELTA[nd]
        w = (x + dx, y + dy)
        next_edge = (v, w)

        if next_edge == start_edge:
            # We are back at the beginning edge; the current path already ends
            # at start_u (since next_edge starts at start_u). Do not re-traverse
            # the start edge; finish here.
            break

        if next_edge in visited_edges:
            # Should not happen if marks pattern yields a single Euler cycle
            raise RuntimeError("Cycle repetition detected before covering all edges.")

        visited_edges.add(next_edge)
        path.append(w)
        u, v = next_edge
        prev_dir = nd

        # Optional early exit guard (should end exactly when all edges are covered)
        if len(visited_edges) > expected:
            raise RuntimeError("Exceeded expected edge count; construction invalid.")

    if len(visited_edges) != expected:
        # Defensive check: the chosen marks should induce a single cycle covering all edges
        raise RuntimeError(
            f"Constructed cycle uses {len(visited_edges)} edges, expected {expected}."
        )

    # At this point, path ends at start_u, forming a closed walk
    return path


def _compress_to_turning_points(path: List[Tuple[int, int]]) -> List[List[int]]:
    """
    Compress a vertex-by-vertex path into turning points, including start and end
    (the end equals the start for this closed tour). Intermediate collinear points
    are omitted.
    """
    if not path:
        return []
    turns: List[List[int]] = [list(path[0])]

    def dir_between(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
        return (b[0] - a[0], b[1] - a[1])

    prev = path[0]
    prev_dir_vec = dir_between(path[0], path[1])

    for i in range(1, len(path) - 1):
        cur = path[i]
        cur_dir_vec = dir_between(path[i], path[i + 1])
        if cur_dir_vec != prev_dir_vec:
            turns.append([cur[0], cur[1]])
            prev_dir_vec = cur_dir_vec
        prev = cur

    # Include the final vertex (which equals the start) as the last turning point
    last = path[-1]
    if turns[-1] != [last[0], last[1]]:
        turns.append([last[0], last[1]])

    return turns


def solution(parameters) -> List[List[int]]:
    """
    Return a list of turning points [[x0,y0], ..., [xK,yK]] whose expansion traverses
    each allowed directed street segment exactly once, obeying the "straight or right"
    rule with right turns forced on the boundary and at marked intersections as per
    the described construction.
    """
    n = int(parameters["n"]) if isinstance(parameters, dict) and "n" in parameters else int(parameters)

    # Build marked points based on n
    marks = _build_marks(n)

    # Generate the full tour as a closed vertex sequence
    full_path = _traverse_full_cycle(n, marks)

    # Compress to turning points
    return _compress_to_turning_points(full_path)
