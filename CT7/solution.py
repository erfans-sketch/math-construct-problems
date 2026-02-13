from typing import Dict, List, Optional
import sys

# We seek a permutation a[1..n] of 1..n such that the absolute displacements
# |a_i - i| are pairwise distinct. This is known to be possible iff n ≡ 0 or 1 (mod 4).
# We construct such a permutation via backtracking with strong heuristics (MRV) and pruning.


def solution(parameters: Dict[str, int]) -> Optional[List[int]]:
    """
    parameters: {'n': int}
    Returns a list a of length n (1-indexed values, 0-indexed Python list) that is a permutation of 1..n
    with all absolute displacements |a[i] - (i+1)| pairwise distinct.

    Returns None if no solution exists (i.e., when n % 4 in {2, 3}).
    """
    n = parameters.get('n')
    if not isinstance(n, int) or n <= 0:
        raise ValueError("parameters['n'] must be a positive integer")

    # Existence condition
    if n % 4 not in (0, 1):
        return None

    # Handle tiny bases quickly
    if n == 1:
        return [1]
    if n == 4:
        return [3, 2, 4, 1]
    if n == 5:
        return [4, 2, 5, 3, 1]

    sys.setrecursionlimit(max(10000, 5 * n))

    # State: a[i] = assigned value at position i (1-based index stored at 0-based i)
    a = [0] * n
    pos_free = [True] * (n + 1)   # positions 1..n free?
    val_free = [True] * (n + 1)   # values 1..n free?

    # Differences remaining to place; we will use MRV to choose next d dynamically
    remaining = set(range(0, n))  # includes 0

    # Precompute for speed: for each d, the set of candidate position-value offsets
    # We don't store dynamic availability here, only structural neighbors per position
    # For generating candidates, we will check current pos_free/val_free

    def gen_candidates_for_d(d: int) -> List[tuple]:
        """Generate feasible (i, j) pairs for current state for a given difference d."""
        pairs = []
        if d == 0:
            # Only (i, i)
            for i in range(1, n + 1):
                if pos_free[i] and val_free[i]:
                    pairs.append((i, i))
            return pairs
        # d > 0
        # Prefer boundary positions to reduce branching
        # We'll iterate positions i that are free and try j=i±d
        # To encourage use of constrained positions, we can check availability of only one option first
        # First pass: positions where only one of i-d or i+d is in [1..n]
        for i in range(1, n + 1):
            if not pos_free[i]:
                continue
            only1 = True
            if i + d <= n and val_free[i + d]:
                pairs.append((i, i + d))
                only1 = False
            if i - d >= 1 and val_free[i - d]:
                # If both directions were available, append this too
                pairs.append((i, i - d))
        # A light ordering heuristic: prioritize pairs touching extremes (values near 1 or n)
        pairs.sort(key=lambda ij: min(ij[0], n + 1 - ij[0], ij[1], n + 1 - ij[1]))
        return pairs

    def has_intersection_pos_val() -> bool:
        """Quick prune for d=0 feasibility: is there any index i with both pos and val free?"""
        # If 0 not remaining, we need not enforce this.
        if 0 not in remaining:
            return True
        # Otherwise, ensure there exists i with pos_free[i] and val_free[i]
        for i in range(1, n + 1):
            if pos_free[i] and val_free[i]:
                return True
        return False

    # Optional memoization of impossible states is complex due to bitsets; skip for simplicity.

    def choose_next_d() -> Optional[int]:
        """Choose the next difference d to assign using MRV (fewest candidates)."""
        best_d = None
        best_count = 10**9
        # Try larger d first in tie, as they are more restrictive
        for d in remaining:
            # quick viability check: if d > 0 and no pair exists structurally, skip
            cands = gen_candidates_for_d(d)
            c = len(cands)
            if c == 0:
                return d  # immediate failure will be detected by caller loop
            if c < best_count or (c == best_count and (best_d is None or d > best_d)):
                best_count = c
                best_d = d
        return best_d

    def backtrack(placed_count: int) -> bool:
        if placed_count == n:
            return True
        # Prune: if zero remains, there must be at least one index with both pos and val free
        if not has_intersection_pos_val():
            return False

        d = choose_next_d()
        if d is None:
            return False
        cands = gen_candidates_for_d(d)
        if not cands:
            return False

        # Try candidates
        remaining.remove(d)
        for (i, j) in cands:
            if not pos_free[i] or not val_free[j]:
                continue
            # Assign
            a[i - 1] = j
            pos_free[i] = False
            val_free[j] = False

            if backtrack(placed_count + 1):
                return True

            # Undo
            a[i - 1] = 0
            pos_free[i] = True
            val_free[j] = True

        remaining.add(d)
        return False

    ok = backtrack(0)
    if not ok:
        return None

    return a


if __name__ == "__main__":
    # Simple sanity checks
    for n in range(1, 21):
        res = solution({'n': n})
        if res is None:
            print(n, '->', None)
        else:
            diffs = [abs(res[i] - (i + 1)) for i in range(n)]
            print(n, 'ok?', len(set(diffs)) == n, 'diffs range:', sorted(diffs)[:5], '...', sorted(diffs)[-5:])
