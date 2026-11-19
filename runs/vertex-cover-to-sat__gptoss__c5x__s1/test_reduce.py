"""Independent tests for reduce.py (VertexCover -> Sat).

We implement brute-force solvers from the problem definitions, then compare
answers on many small instances.  We also check the *polynomial time*
requirement, which is part of the task specification.
"""
from __future__ import annotations

import itertools
import random
import time

from problems import VertexCover, Sat
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Brute-force solvers (from the docstrings, no solvers are provided)

def vertex_cover_solve(inst):
    """Yes iff some vertex set of size <= k covers every edge."""
    n = inst["n"]
    edges = inst["edges"]
    k = inst["k"]
    if k < 0:
        return False
    # Try every subset of vertices of size <= k (k small in tests).
    for size in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), size):
            s = set(subset)
            if all(u in s or v in s for u, v in edges):
                return True
    return False


def sat_solve(inst):
    """Yes iff some assignment satisfies all clauses."""
    m = inst["num_vars"]
    clauses = inst["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def random_vc_instance(rng, max_n=6):
    n = rng.randint(0, max_n)
    all_pairs = list(itertools.combinations(range(n), 2))
    rng.shuffle(all_pairs)
    m = rng.randint(0, len(all_pairs))
    edges = [list(p) for p in all_pairs[:m]]
    # occasionally flip an edge orientation
    for e in edges:
        if rng.random() < 0.5:
            e.reverse()
    k = rng.randint(-2, n + 1)
    return {"n": n, "edges": edges, "k": k}


# ----------------------------------------------------------------------
# Test harness

RESULTS = []


def record(name, passed, detail=""):
    RESULTS.append((name, passed, detail))
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name} {detail}")


def test_correctness_random():
    rng = random.Random(12345)
    mismatches = []
    count = 0
    for _ in range(4000):
        inst = random_vc_instance(rng)
        VertexCover.validate(inst)
        out = reduce_mod.reduce(inst)
        Sat.validate(out)  # reduction output must be a valid SAT instance
        a = vertex_cover_solve(inst)
        b = sat_solve(out)
        count += 1
        if a != b:
            mismatches.append((inst, out, a, b))
            if len(mismatches) >= 5:
                break
    record("correctness_random", not mismatches,
           f"({count} instances, {len(mismatches)} mismatches)")


def test_edge_cases():
    cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -1},
        {"n": 5, "edges": [], "k": 0},
        {"n": 5, "edges": [], "k": -3},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 0},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 1},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 4},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 100},
    ]
    bad = []
    for inst in cases:
        VertexCover.validate(inst)
        out = reduce_mod.reduce(inst)
        Sat.validate(out)
        if vertex_cover_solve(inst) != sat_solve(out):
            bad.append(inst)
    record("edge_cases", not bad, f"({len(cases)} cases, {len(bad)} wrong)")


def test_k_negative_unsat():
    inst = {"n": 3, "edges": [[0, 1]], "k": -1}
    out = reduce_mod.reduce(inst)
    Sat.validate(out)
    record("k_negative_unsat", sat_solve(out) is False, f"out={out}")


def test_output_validity():
    rng = random.Random(999)
    bad = []
    for _ in range(500):
        inst = random_vc_instance(rng)
        try:
            out = reduce_mod.reduce(inst)
            Sat.validate(out)
        except Exception as exc:  # noqa: BLE001
            bad.append((inst, repr(exc)))
    record("output_validity", not bad, f"({len(bad)} invalid outputs)")


# ----------------------------------------------------------------------
# Complexity: the task requires reduce() to run in POLYNOMIAL time.

def clause_count(n, k):
    out = reduce_mod.reduce({"n": n, "edges": [], "k": k})
    return len(out["clauses"])


def test_polynomial_size():
    """Output size must be polynomial in the input size.

    Input size ~ n + |E|.  A polynomial reduction should have output size
    bounded by some polynomial.  We check against n**4 (generous) for
    k = n//2 and show the growth is super-polynomial.
    """
    rows = []
    poly_ok = True
    for n in (10, 14, 18, 20):
        k = n // 2
        c = clause_count(n, k)
        bound = n ** 4
        rows.append((n, k, c, bound))
        if c > bound:
            poly_ok = False
    detail = "; ".join(f"n={n},k={k}: clauses={c} vs n^4={b}" for n, k, c, b in rows)
    record("polynomial_output_size", poly_ok, "(" + detail + ")")


def test_polynomial_time_empirical():
    """Empirically measure growth of reduce() runtime for k=n//2."""
    times = []
    for n in (12, 16, 18):
        k = n // 2
        t0 = time.time()
        clause_count(n, k)
        times.append((n, time.time() - t0))
    # A polynomial-time algorithm should not blow up this fast; the ratio
    # per +2 in n should be bounded by a polynomial factor.  We flag if the
    # time grows by more than ~6x per +2 (exponential-ish).
    growth_ok = True
    for i in range(1, len(times)):
        prev = times[i - 1][1]
        cur = times[i][1]
        if prev > 0 and cur / prev > 6:
            growth_ok = False
    detail = "; ".join(f"n={n}: {t:.4f}s" for n, t in times)
    record("polynomial_time_empirical", growth_ok, "(" + detail + ")")



def test_exponential_growth():
    """Clause count for k=n//2 must grow super-polynomially.

    A polynomial reduction would keep the output size polynomial in n.
    Here the count is C(n, n//2+1), which grows exponentially.
    """
    import math
    counts = []
    for n in (18, 20, 22, 24):
        k = n // 2
        counts.append((n, clause_count(n, k)))
    # Check that the count is at least exponential in n: ratio when n -> n+2
    # should be roughly 4x for the central binomial coefficient.
    exp_ok = all(counts[i][1] > 2 * counts[i - 1][1] for i in range(1, len(counts)))
    # And confirm it equals C(n, k+1)
    formula_ok = all(c == math.comb(n, n // 2 + 1) for n, c in counts)
    detail = "; ".join(f"n={n}: {c}" for n, c in counts)
    record("exponential_growth", exp_ok and formula_ok, "(" + detail + ")")


def main():
    test_correctness_random()
    test_edge_cases()
    test_k_negative_unsat()
    test_output_validity()
    test_polynomial_size()
    test_polynomial_time_empirical()
    test_exponential_growth()

    total = len(RESULTS)
    passed = sum(1 for _, p, _ in RESULTS if p)
    print(f"\nSUMMARY: {passed}/{total} tests passed")
    return total, passed


if __name__ == "__main__":
    main()
