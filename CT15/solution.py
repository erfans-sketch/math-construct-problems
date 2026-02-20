import math
from typing import List, Tuple, Dict, Any


def _arc_points(n: int, R: float, theta_deg: float = 60.0) -> List[Tuple[float, float]]:
    """
    Generate n points on a circular arc of total angle `theta_deg` (in degrees),
    forming an up-facing convex curve located below the top segment.

    We parameterize the arc using angle a in [-theta/2, +theta/2] with the circle
    centered at (0, -R), so the arc lies roughly in y ∈ [-0.5R, 0].
    Points are ordered from left to right.
    """
    if n <= 0:
        raise ValueError("n must be >= 1 for the bottom arc")

    theta = math.radians(theta_deg)
    # Use parameterization: (x, y) = (R*sin(a), -R + R*cos(a)) for a in [-theta/2, theta/2]
    a0 = -theta / 2.0
    a1 = +theta / 2.0
    if n == 1:
        a_values = [0.0]
    else:
        step = (a1 - a0) / (n - 1)
        a_values = [a0 + i * step for i in range(n)]

    pts = [(R * math.sin(a), -R + R * math.cos(a)) for a in a_values]
    return pts


def solution(parameters: Dict[str, Any]):
    """
    Construct a simple polygon that can be triangulated in exactly n ways.

    Idea used:
    - Create an up-facing convex chain of n vertices along a 120° circular arc placed at the bottom.
    - Add two top vertices on a horizontal segment above the arc, at a distance comparable
      to the chord length of the arc, then walk the polygon along the arc (left→right),
      go to the top-right vertex, then top-left, and close back to the leftmost arc vertex.

    parameters: {"n": int}
    returns: list of [x, y] pairs representing the polygon vertex sequence
    """
    n = int(parameters.get("n", 5))
    if n < 1:
        # For n <= 0, fall back to n=1 which yields a triangle (1 triangulation)
        n = 1

    # Choose a radius large enough to avoid numerical degeneracies for bigger n
    R = max(10.0, 0.6 * n)

    # Bottom arc with n vertices (left to right order)
    bottom = _arc_points(n=n, R=R, theta_deg=60.0)

    # Determine the horizontal span of the arc to place the two top vertices wider than the arc
    x_left_arc = bottom[0][0]
    x_right_arc = bottom[-1][0]
    chord_len = abs(x_right_arc - x_left_arc)

    # Place the top segment high enough so every diagonal from each top vertex
    # to any bottom vertex remains strictly inside the polygon. Use a generous height
    # that scales with chord length (and thus with R and n).
    # Per request: place the top segment at a vertical distance equal to
    # twice the diagonal (we take the chord length of the arc as the diagonal).
    y_top = 2.0 * chord_len if chord_len > 0 else 2.0 * R

    # Make the top segment noticeably wider than the arc to avoid borderline cases
    # for large n where some diagonals could slightly exit the polygon.
    margin = 0.6 * chord_len if chord_len > 0 else 0.5 * R
    x_left_top = x_left_arc - margin
    x_right_top = x_right_arc + margin

    top_right = (x_right_top, y_top)
    top_left = (x_left_top, y_top)

    # Vertex order: walk along the arc (left → right), then top-right, then top-left, and close.
    poly = bottom + [top_right, top_left]

    # Return as list of [x, y] to be robust to JSON serialization downstream
    return [[float(x), float(y)] for (x, y) in poly]
