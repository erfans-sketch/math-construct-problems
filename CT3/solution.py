import math
from typing import List, Tuple, Optional

Point = Tuple[float, float]
Segment = Tuple[Point, Point]

def _regular_polygon(k: int, R: float, center: Point, start_angle: float) -> List[Point]:
    cx, cy = center
    return [
        (cx + R * math.cos(start_angle + 2.0 * math.pi * i / k),
         cy + R * math.sin(start_angle + 2.0 * math.pi * i / k))
        for i in range(k)
    ]

def _cross(ax: float, ay: float, bx: float, by: float) -> float:
    return ax * by - ay * bx

def _segment_intersection(p: Point, p2: Point, q: Point, q2: Point, eps: float = 1e-12) -> Optional[Point]:
    """
    Proper intersection point of segments p->p2 and q->q2 (excluding endpoints).
    Returns None if they don't intersect properly.
    """
    px, py = p
    rx, ry = (p2[0] - px, p2[1] - py)
    qx, qy = q
    sx, sy = (q2[0] - qx, q2[1] - qy)

    rxs = _cross(rx, ry, sx, sy)
    q_p_x, q_p_y = (qx - px, qy - py)

    if abs(rxs) < eps:  # parallel or collinear
        return None

    t = _cross(q_p_x, q_p_y, sx, sy) / rxs
    u = _cross(q_p_x, q_p_y, rx, ry) / rxs

    # Proper intersection strictly inside both segments (exclude endpoints)
    if eps < t < 1.0 - eps and eps < u < 1.0 - eps:
        return (px + t * rx, py + t * ry)
    return None

def davids_star_boundary_vertices(
    k: int,
    R: float = 1.0,
    center: Point = (0.0, 0.0),
    start_angle: float = 0.0,
    eps: float = 1e-10,
) -> List[Point]:
    """
    Boundary vertices of the "generalized David's star" defined as the union of:
      - a regular k-gon
      - another regular k-gon rotated by pi/k

    For k=3, this returns a 12-gon (the classic Star of David outline).
    In general, you typically get 4k boundary vertices: 2k original vertices + 2k edge intersections.

    Output is in cyclic (CCW) order around the center, suitable for a polygonal chain.

    Notes:
      - This returns the OUTER boundary of the union (a simple star-like polygon).
      - Works best for k >= 3.
    """
    if not isinstance(k, int) or k < 3:
        raise ValueError("k must be an integer >= 3")

    # Two rotated regular k-gons
    A = _regular_polygon(k, R, center, start_angle)
    B = _regular_polygon(k, R, center, start_angle + math.pi / k)

    # Build edge lists
    A_edges: List[Segment] = [(A[i], A[(i + 1) % k]) for i in range(k)]
    B_edges: List[Segment] = [(B[i], B[(i + 1) % k]) for i in range(k)]

    # Compute all proper intersections between edges of A and edges of B
    inters: List[Point] = []
    for (p, p2) in A_edges:
        for (q, q2) in B_edges:
            x = _segment_intersection(p, p2, q, q2)
            if x is not None:
                inters.append(x)

    # Deduplicate intersections (floating-point tolerance)
    def key(pt: Point) -> Tuple[int, int]:
        return (int(round(pt[0] / eps)), int(round(pt[1] / eps)))

    uniq = {}
    for pt in inters:
        uniq[key(pt)] = pt
    inters = list(uniq.values())

    # Combine polygon vertices + intersection points
    pts = A + B + inters

    # Deduplicate combined points too
    uniq2 = {}
    for pt in pts:
        uniq2[key(pt)] = pt
    pts = list(uniq2.values())

    cx, cy = center

    # Sort by polar angle around the center -> cyclic order
    pts.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))

    return pts




import math
from typing import List, Tuple, Optional

Point = Tuple[float, float]
Segment = Tuple[Point, Point]

# --- assumes you already have davids_star_boundary_vertices from before ---
# (If not, paste your previous implementation above this.)

def _midpoint(a: Point, b: Point) -> Point:
    return ((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5)

def _cross(ax: float, ay: float, bx: float, by: float) -> float:
    return ax * by - ay * bx

def _rotate_vec(v: Point, ang: float) -> Point:
    x, y = v
    c, s = math.cos(ang), math.sin(ang)
    return (c * x - s * y, s * x + c * y)

def _segment_line_intersection(a: Point, b: Point, p: Point, r: Point, eps: float = 1e-12) -> Optional[Point]:
    """
    Intersection of segment a->b with infinite line p + t r.
    Returns None if no intersection within the segment (with eps slack) or parallel.
    """
    s = (b[0] - a[0], b[1] - a[1])
    rxs = _cross(s[0], s[1], r[0], r[1])
    if abs(rxs) < eps:
        return None
    p_a = (p[0] - a[0], p[1] - a[1])
    u = _cross(p_a[0], p_a[1], r[0], r[1]) / rxs
    if -eps <= u <= 1.0 + eps:
        return (a[0] + u * s[0], a[1] + u * s[1])
    return None

def _ray_line_intersection_from_b(a: Point, b: Point, p: Point, r: Point, eps: float = 1e-12) -> Optional[Point]:
    """
    Intersection of the infinite line through a->b with p+tr,
    constrained to the ray that starts at b and goes forward in direction (b-a).
    """
    s = (b[0] - a[0], b[1] - a[1])  # direction a->b
    rxs = _cross(s[0], s[1], r[0], r[1])
    if abs(rxs) < eps:
        return None
    p_a = (p[0] - a[0], p[1] - a[1])
    u = _cross(p_a[0], p_a[1], r[0], r[1]) / rxs  # along a->b
    # b corresponds to u=1; forward beyond b means u >= 1
    if u < 1.0 - eps:
        return None
    return (a[0] + u * s[0], a[1] + u * s[1])


#########################################################################
def add_sharpnel(pts: List[Point], eps: float = 1e-10) -> List[Point]:
    """
    Take pts = davids_star_boundary_vertices(k, ...), and INSERT the 7 points
    exactly once, in the specific place you described (between pts[2] and pts[4] area):

      q1 = midpoint(pts[0], pts[1])
      l1 through q1 parallel to segment pts[2]pts[4]
      l2 through q1 rotated by + 2*pi/(4k) relative to l1
      q2 = l1 ∩ segment pts[2]pts[3]
      q3 = l2 ∩ segment pts[2]pts[3]
      q4 = l1 ∩ segment pts[3]pts[4]
      q5 = l2 ∩ segment pts[3]pts[4]
      q6 = l1 ∩ extension of pts[4]pts[5] beyond pts[5]
      q7 = l2 ∩ extension of pts[4]pts[5] beyond pts[5]

    New cyclic order (one-time modification):
      pts[0], pts[1], pts[2], q3, q1, q2, pts[3], q4, q6, q7, q5, pts[4], pts[5], pts[6], ...

    Returns the modified polygon vertex list in cyclic order.
    """
    n = len(pts)
    if n < 6:
        raise ValueError("Need at least 6 boundary points.")

    # --- build the new points from the given indices ---
    q1 = _midpoint(pts[1], pts[3])

    # l1 direction parallel to pts[2]pts[4]
    d1 = (pts[4][0] - pts[2][0], pts[4][1] - pts[2][1])
    if abs(d1[0]) < 1e-18 and abs(d1[1]) < 1e-18:
        raise ValueError("Degenerate direction for l1 (pts[2] and pts[4] coincide).")

    # l2 rotated by + 2*pi/(4k)
    ang = 2.0 * math.pi / (8.0 * n)
    d2 = _rotate_vec(d1, ang)

    # intersections with segments
    q2 = _segment_line_intersection(pts[2], pts[3], q1, d1, eps=eps)
    q3 = _segment_line_intersection(pts[2], pts[3], q1, d2, eps=eps)
    q4 = _segment_line_intersection(pts[3], pts[4], q1, d1, eps=eps)
    q5 = _segment_line_intersection(pts[3], pts[4], q1, d2, eps=eps)


    # intersections with extension beyond pts[5] along pts[4]->pts[5]
    q6 = _ray_line_intersection_from_b(pts[6], pts[5], q1, d1, eps=eps)
    q7 = _ray_line_intersection_from_b(pts[6], pts[5], q1, d2, eps=eps)
    if any(x is None for x in (q2, q3, q4, q5, q6, q7)):
        raise ValueError(
            "Failed to compute one or more intersections (degenerate or near-parallel configuration)."
        )

    # --- splice into the cyclic order exactly once ---
    # Original: pts[0], pts[1], pts[2], pts[3], pts[4], pts[5], ...
    # New:      pts[0], pts[1], pts[2], q3, q1, q2, pts[3], q4, q6, q7, q5, pts[4], pts[5], ...
    new_pts: List[Point] = []
    new_pts.extend([pts[0], pts[1], pts[2], q3, q1, q2, pts[3], q4, q6, q7, q5, pts[4]])
    new_pts.extend(pts[5:])  # continue with the rest unchanged

    # optional: remove accidental consecutive duplicates due to numeric issues
    def close(a: Point, b: Point) -> bool:
        return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 <= (10 * eps) ** 2

    cleaned: List[Point] = []
    for p in new_pts:
        if not cleaned or not close(cleaned[-1], p):
            cleaned.append(p)
    if cleaned and close(cleaned[0], cleaned[-1]):
        cleaned.pop()

    return cleaned

##########################################################################

def solution(parameters):
    n = parameters.get("n")
    if isinstance(n, int) and n >= 12 and n % 4 == 0:
        k = n // 4
        pts = davids_star_boundary_vertices(k)
        return pts

    if isinstance(n, int) and n >= 19 and n % 4 == 3:
        k = (n - 7) // 4
        pts = davids_star_boundary_vertices(k)
        pts_with_sharpnel = add_sharpnel(pts)
        return pts_with_sharpnel
    
    if isinstance(n, int) and n >= 26 and n % 4 == 2:
        k = (n - 14) // 4
        pts = davids_star_boundary_vertices(k)
        pts_with_sharpnel = add_sharpnel(pts)
        s = 2*(k//2+1)
        pts_with_sharpnel = pts_with_sharpnel[-s:] + pts_with_sharpnel[:-s]
        pts_with_sharpnel_twice = add_sharpnel(pts_with_sharpnel)
        return pts_with_sharpnel_twice

    if isinstance(n, int) and n >= 33 and n % 4 == 1:
        k = (n - 21) // 4
        pts = davids_star_boundary_vertices(k)
        pts_with_sharpnel = add_sharpnel(pts)
        s = 2*(k//2+1)
        pts_with_sharpnel = pts_with_sharpnel[-s:] + pts_with_sharpnel[:-s]
        pts_with_sharpnel_twice = add_sharpnel(pts_with_sharpnel)
        pts_with_sharpnel_twice = pts_with_sharpnel_twice[-s:] + pts_with_sharpnel_twice[:-s]
        pts_with_sharpnel_trice = add_sharpnel(pts_with_sharpnel_twice)
        return pts_with_sharpnel_trice

    raise ValueError("Invalid value for parameter 'n'.")
