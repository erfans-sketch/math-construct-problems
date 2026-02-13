def solution(parameters):
    """
    Construct an (m+1) x (n+1) labeling matrix for K_{m,n}.

    Label choices (as requested):
      - Column-part vertices (top row, excluding [0,0]): 1..n
      - Row-part vertices (first column, excluding [0,0]): (n+1), 2(n+1), ..., m(n+1)
      - Constant C = (n+1)(m+2)
      - Edge (i,j) label = C - row_vertex_i - col_vertex_j

    Returns a list of lists with matrix[0][0] = 0.
    """
    m = int(parameters.get("m", 1))
    n = int(parameters.get("n", 1))
    if m <= 0 or n <= 0:
        raise ValueError("m and n must be positive integers")

    # Vertex labels
    col_vertices = list(range(1, n + 1))
    row_vertices = [i * (n + 1) for i in range(1, m + 1)]

    # Constant
    C = (n + 1) * (m + 2)

    # Initialize matrix with zeros
    matrix = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

    # Place column vertex labels (top row, excluding [0,0])
    for j in range(n):
        matrix[0][j + 1] = col_vertices[j]

    # Place row vertex labels (first column, excluding [0,0])
    for i in range(m):
        matrix[i + 1][0] = row_vertices[i]

    # Compute and place edge labels in the inner m x n block
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            matrix[i][j] = C - matrix[i][0] - matrix[0][j]

    return matrix
