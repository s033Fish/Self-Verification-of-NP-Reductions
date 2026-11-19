"""Independent checks of reduce.py (3-SAT -> Vertex Cover).

Brute-force solvers for both problems are implemented directly from the
definitions in problems.py; their answers are compared on many small
instances and on the instances produced by reduce.py.

The vertex-cover solver is an exact branch-and-bound using a maximal
matching lower bound, so it stays fast on the small graphs produced here.
"""

from __future__ import annotations

import itertools
import random
import sys

from problems import ThreeSat, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, written from the problem definitions.

def solve_three_sat(instance):
    """True iff some assignment satisfies every clause."""
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def _max_matching_size(edges):
    """Greedy maximal matching size (a valid lower bound on VC)."""
    used = set()
    size = 0
    for u, v in edges:
        if u not in used and v not in used:
            used.add(u)
            used.add(v)
            size += 1
    return size


def solve_vertex_cover(instance):
    """True iff there is a vertex cover of size at most k (exact)."""
    VertexCover.validate(instance)
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    if not edges:
        return True
    budget = min(k, n)

    def rec(remaining, b):
        if not remaining:
            return True
        if b <= 0:
            return False
        if _max_matching_size(remaining) > b:
            return False
        u, v = remaining[0]
        for pick in (u, v):
            nxt = [e for e in remaining if e[0] != pick and e[1] != pick]
            if rec(nxt, b - 1):
                return True
        return False

    return rec(edges, budget)


# ----------------------------------------------------------------------
# Test harness.

class Counter:
    def __init__(self):
        self.run = 0
        self.passed = 0
        self.failures = []

    def check(self, condition, message):
        self.run += 1
        if condition:
            self.passed += 1
        else:
            self.failures.append(message)


def check_instance(counter, instance, label=""):
    """Compare source answer with the answer of its reduction."""
    src = solve_three_sat(instance)
    target = reduce(instance)
    try:
        VertexCover.validate(target)
        valid = True
    except Exception as exc:  # noqa: BLE001
        valid = False
        counter.check(False, f"{label}: target invalid: {exc} ({instance})")
    if valid:
        tgt = solve_vertex_cover(target)
        counter.check(
            src == tgt,
            f"{label}: mismatch src={src} tgt={tgt} instance={instance} "
            f"target={target}",
        )
    # reduce must be deterministic / repeatable.
    counter.check(
        reduce(instance) == target,
        f"{label}: reduce not deterministic for {instance}",
    )


def random_clause(m, rng):
    vs = rng.sample(range(1, m + 1), 3)
    return [v if rng.random() < 0.5 else -v for v in vs]


def random_instance(m, max_c, rng):
    if m < 3:
        return {"num_vars": m, "clauses": []}
    c = rng.randint(0, max_c)
    return {"num_vars": m, "clauses": [random_clause(m, rng) for _ in range(c)]}


def all_clauses_for(m):
    out = []
    for combo in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product((1, -1), repeat=3):
            out.append([s * v for s, v in zip(signs, combo)])
    return out


def main():
    counter = Counter()
    rng = random.Random(12345)

    # --- Edge cases -----------------------------------------------------
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        # All 8 clauses over 3 vars: unsatisfiable.
        {"num_vars": 3, "clauses": [
            [a, b, c]
            for a in (1, -1)
            for b in (2, -2)
            for c in (3, -3)
        ]},
        # Duplicate clauses (allowed).
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
        # Variables need not all appear.
        {"num_vars": 6, "clauses": [[1, 2, 3]]},
        # Forced assignment (unsat).
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3]]},
    ]
    for i, inst in enumerate(edge_cases):
        check_instance(counter, inst, f"edge{i}")

    # --- Exhaustive over small formulas ---------------------------------
    # m=3: every multiset of up to 4 clauses from all 8 possible clauses.
    for m in (1, 2, 3):
        all_cl = all_clauses_for(m)
        max_c = 4 if m == 3 else 2
        for c in range(0, max_c + 1):
            for chosen in itertools.combinations_with_replacement(all_cl, c):
                inst = {"num_vars": m, "clauses": [list(cl) for cl in chosen]}
                check_instance(counter, inst, f"exh-m{m}-c{c}")

    # m=4: every multiset of up to 2 clauses from all 32 possible clauses.
    all4 = all_clauses_for(4)
    for c in range(0, 3):
        for chosen in itertools.combinations_with_replacement(all4, c):
            inst = {"num_vars": 4, "clauses": [list(cl) for cl in chosen]}
            check_instance(counter, inst, f"exh-m4-c{c}")

    # --- Random instances ----------------------------------------------
    for _ in range(3000):
        m = rng.randint(0, 4)
        inst = random_instance(m, 4, rng)
        check_instance(counter, inst, "rand")

    for _ in range(1500):
        m = rng.randint(3, 7)
        inst = random_instance(m, 8, rng)
        check_instance(counter, inst, "rand2")

    # --- Structured satisfiable / unsatisfiable -------------------------
    for m in (3, 4, 5):
        clauses = []
        for v in range(1, m + 1):
            others = [u for u in range(1, m + 1) if u != v][:2]
            clauses.append([v, others[0], others[1]])
            clauses.append([-v, others[0], others[1]])
        check_instance(counter, {"num_vars": m, "clauses": clauses}, "forced-unsat")

    # ------------------------------------------------------------------
    print(f"tests_run    = {counter.run}")
    print(f"tests_passed = {counter.passed}")
    if counter.failures:
        print(f"FAILURES ({len(counter.failures)}):")
        for f in counter.failures[:20]:
            print("  -", f)
        sys.exit(1)
    print("ALL TESTS PASSED")
    return counter


if __name__ == "__main__":
    main()
