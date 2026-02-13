import math
from typing import Dict, List, Union


def _max_binom(m_minus_1: int) -> int:
	"""Return max_j C(m-1, j)."""
	j = (m_minus_1) // 2
	return math.comb(m_minus_1, j)


def _choose_Z(m: int) -> int:
	"""Find a sufficiently large integer Z so that for all i in [1..m],
	the base-b_i representation of n has exactly m digits with no carries,
	where
		K = m! * Z,
		n = K^{m-1},
		b_i = K/i - 1.

	It suffices to ensure for all i and all j:
		i^{m-1} * C(m-1, j) <= b_i - 1 = (m!/i) * Z - 2.

	A safe global bound is achieved by maximizing the RHS requirement over i and j.
	We use Cmax = max_j C(m-1, j) = C(m-1, floor((m-1)/2)).
	Then require:
		(m!/i) * Z >= i^{m-1} * Cmax + 2  for all i
	  => m! * Z >= i^m * Cmax + 2i        for all i
	  => m! * Z >= m^m * Cmax + 2m        (worst case i=m).

	Thus choose Z = ceil((m^m * Cmax + 2m) / m!)
	and add a small margin (+1) to be conservative.
	"""
	if m <= 0:
		raise ValueError("m must be positive")
	if m == 1:
		# Trivial, but our tasks use m >= 2. Keep consistent anyway.
		return 2
	Cmax = _max_binom(m - 1)
	numer = (m ** m) * Cmax + 2 * m
	denom = math.factorial(m)
	Z = (numer + denom - 1) // denom  # ceil(numer/denom)
	return max(Z + 1, 2)


def construct_palindromic_bases(m: int) -> Dict[str, Union[int, List[int]]]:
	"""Implements the construction:
		Let K = m! * Z for sufficiently large Z, choose
			n = K^{m-1}
			a_i = K/i - 1  for i=1..m
		Then, in base a_i, n expands as the binomial digits of (b_i+1)^{m-1}
		scaled by i^{m-1}, which are symmetric; with our Z, all digits are < base
		so no carries occur, giving an m-digit palindrome in every chosen base.
	"""
	if m < 2:
		raise ValueError("m must be >= 2")

	Z = _choose_Z(m)
	K = math.factorial(m) * Z
	n = pow(K, m - 1)
	# Bases a_i = K/i - 1 for i=1..m
	a: List[int] = []
	for i in range(1, m + 1):
		# K is divisible by i since K = m! * Z
		base = K // i - 1
		if base <= 1:
			# This should not happen with our Z, but guard anyway by increasing Z.
			# Double Z and recompute.
			Z = max(Z * 2, 2)
			K = math.factorial(m) * Z
			n = pow(K, m - 1)
			a = []
			# restart computation of bases with larger Z
			for ii in range(1, m + 1):
				base2 = K // ii - 1
				if base2 <= 1:
					raise RuntimeError("Failed to choose a valid Z producing bases > 1.")
				a.append(base2)
			break
		a.append(base)

	# Ensure distinctness (should hold since K/i distinct for i=1..m)
	if len(set(a)) != m:
		# Rarely, if something went wrong, bump Z and retry once.
		Z = max(Z * 2, 2)
		K = math.factorial(m) * Z
		n = pow(K, m - 1)
		a = [K // i - 1 for i in range(1, m + 1)]
		if len(set(a)) != m:
			raise RuntimeError("Failed to construct distinct bases.")

	return {"n": int(n), "a": [int(x) for x in a]}


def solution(parameters: Dict[str, int]):
	m = int(parameters.get("m", 4))
	return construct_palindromic_bases(m)

