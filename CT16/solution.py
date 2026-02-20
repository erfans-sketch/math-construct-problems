import random

def _segments_intersect(p1, p2, q1, q2):
    """Check if segments p1-p2 and q1-q2 intersect (excluding endpoints)."""

    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

    return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)


# Required. DO NOT CHANGE FUNCTION NAME. always use 'verify'
def _verify(construction, parameters):
    """
    Verify that the given list of indices forms a simple polygon from the given points.

    :param construction: a list of integers representing the vertex order
    :return: tuple (bool, str)
    """
    n = parameters["n"]
    points = parameters["point_positions"]

    if len(construction) != n:
        return False, f"Incorrect. Polygon must have {n} vertices"

    # Check all indices are valid
    if set(construction) != set(points.keys()):
        return False, "Incorrect. Polygon must use all given points exactly once"

    # Build list of polygon edges
    edges = [(points[construction[i]], points[construction[(i + 1) % n]]) for i in range(n)]

    # Check for intersections between non-adjacent edges
    for i, (p1, p2) in enumerate(edges):
        for j, (q1, q2) in enumerate(edges):
            if abs(i - j) in (0, 1, n - 1):  # adjacent edges are allowed to meet
                continue
            if _segments_intersect(p1, p2, q1, q2):
                return False, f"Incorrect. Edges {i+1} and {j+1} intersect"

    return True, "Correct Answer"


def _generate_random_construction(parameters):
    """Generates a random order of points (may not form a simple polygon)."""
    indices = list(parameters["point_positions"].keys())
    random.shuffle(indices)
    return indices


def solution(parameters):
    n = parameters["n"]
    points = parameters["point_positions"]

    # Start with a random permutation
    construction = _generate_random_construction(parameters)

    def get_edges(order):
        return [
            (points[order[i]], points[order[(i + 1) % n]])
            for i in range(n)
        ]

    max_iterations = 5000
    for _ in range(max_iterations):

        ok, _ = _verify(construction, parameters)
        if ok:
            return construction

        edges = get_edges(construction)

        fixed = False
        # look for the first intersecting non-adjacent pair
        for i in range(n):
            p1, p2 = edges[i]
            for j in range(i + 1, n):
                # skip adjacent and identical edges
                if abs(i - j) in (0, 1, n - 1):
                    continue

                q1, q2 = edges[j]

                if _segments_intersect(p1, p2, q1, q2):
                    # untangle by reversing the vertex order between i+1 and j
                    i1 = (i + 1) % n
                    j1 = (j + 1) % n

                    if i1 < j1:
                        construction[i1:j1] = reversed(construction[i1:j1])
                    else:
                        # wrap-around reversal
                        mid = construction[i1:] + construction[:j1]
                        mid.reverse()
                        k = 0
                        for t in range(i1, n):
                            construction[t] = mid[k]
                            k += 1
                        for t in range(0, j1):
                            construction[t] = mid[k]
                            k += 1

                    fixed = True
                    break
            if fixed:
                break

        # if nothing changed, reshuffle and retry
        if not fixed:
            construction = _generate_random_construction(parameters)

    # fallback (should almost never happen)
    return construction