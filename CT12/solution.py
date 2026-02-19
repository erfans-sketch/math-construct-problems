def solution(parameters):
    """
    Find an integer n > M such that n^3 - 2 is a sum of two integer squares.

    Idea: Let n = m^2 + 2. Then
        n^3 - 2 = (m^3 + 3m)^2 + (3m^2 + 6).
    If 3m^2 + 6 is a perfect square (say t^2), then n^3 - 2 = (m^3 + 3m)^2 + t^2
    is a sum of two squares. This reduces to solving the Pell-type equation
        t^2 - 3 m^2 = 6.
    All solutions (t, m) are generated from the base solution (3, 1) via
        (t_{k+1}, m_{k+1}) = (2 t_k + 3 m_k, t_k + 2 m_k),
    since multiplying by (2 + sqrt(3)) preserves norm.
    We iterate until n = m^2 + 2 exceeds M.
    """
    M = parameters.get("M", 1)
    if not isinstance(M, int):
        try:
            M = int(M)
        except Exception:
            M = 1

    # Start from minimal positive solution to t^2 - 3 m^2 = 6
    t, m = 3, 1

    # If needed, iterate via the Pell unit (2 + sqrt(3)) to get larger m
    # Recurrence:
    #   t' = 2 t + 3 m
    #   m' = t + 2 m
    # Stop when n = m^2 + 2 > M
    for _ in range(10000):  # generous safety bound
        n = m * m + 2
        if n > M:
            return n
        t, m = 2 * t + 3 * m, t + 2 * m

    # Fallback (should never happen for reasonable M)
    return m * m + 2
