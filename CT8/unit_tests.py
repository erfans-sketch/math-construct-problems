import json
import ast
import numpy as np
import pytest


def _parse_matrix(construction):
    if isinstance(construction, str):
        s = construction.strip()
        # Strip simple code fences if present
        if s.startswith("```"):
            lines = s.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            s = "\n".join(lines).strip()
        obj = None
        try:
            obj = json.loads(s)
        except Exception:
            try:
                obj = ast.literal_eval(s)
            except Exception as e:
                pytest.fail(f"Could not parse submission. Provide a 2D array or its JSON. Error: {e}")
        construction = obj
    try:
        matrix = np.array(construction, dtype=object)
    except Exception as e:
        pytest.fail(f"Could not convert construction to matrix: {e}")
    return matrix


def test_dimensions(construction, parameters):
    m = int(parameters["m"])
    n = int(parameters["n"]) 
    matrix = _parse_matrix(construction)
    assert matrix.shape == (m + 1, n + 1), (
        f"Incorrect dimensions: expected {(m+1, n+1)}, got {matrix.shape}"
    )


def test_entries_are_integers(construction, parameters):
    matrix = _parse_matrix(construction)
    try:
        _ = [int(x) for row in matrix.tolist() for x in row][1:]
    except Exception:
        pytest.fail("All entries must be integers.")


def test_label_range_and_distinct(construction, parameters):
    m = int(parameters["m"])
    n = int(parameters["n"]) 
    matrix = _parse_matrix(construction)
    entries = [int(x) for row in matrix.tolist() for x in row][1:]
    max_label = m * n + m + n
    assert all(1 <= x <= max_label for x in entries), (
        f"Labels must be in range 1..{max_label}."
    )
    assert len(set(entries)) == len(entries), "Labels are not distinct."


def test_magic_property(construction, parameters):
    m = int(parameters["m"])
    n = int(parameters["n"]) 
    matrix = _parse_matrix(construction)
    mat = np.array(matrix, dtype=int)
    row_vertices = mat[1:, 0]
    col_vertices = mat[0, 1:]
    edge_labels = mat[1:, 1:]

    target_sum = None
    for i in range(m):
        for j in range(n):
            total = int(edge_labels[i, j]) + int(row_vertices[i]) + int(col_vertices[j])
            if target_sum is None:
                target_sum = total
            else:
                assert total == target_sum, (
                    f"Magic property violated at edge ({i+1},{j+1}): expected {target_sum}, got {total}."
                )
