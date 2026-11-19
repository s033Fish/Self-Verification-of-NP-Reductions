"""Independent tests for reduce.py (Hamiltonian Cycle -> SAT).

We implement our own brute-force solvers for both problems from the
definitions in problems.py, generate many small source instances, run
reduce() on each, and check that the answers agree.  We also validate
that every produced target instance is a well-formed Sat instance.
"""

from __future__ import annotations

import itertools
import json
import random
import sys

from problems import HamiltonianCycle, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solver for Hamiltonian Cycle
# ----------------------------------------------------------------------

def hamiltonian_yes(n, edges):
    if n <= 2:
        return False
    adj = set()
    for u, v in edges:
        adj.add(frozenset((u, v)))
    # Fix vertex 0 at the first position; try all orderings of the rest.
    for perm in itertools.permutations(range(1, n)):
        order = (0,) + perm
        ok = True
        for i in range(n):
            a = order[i]
            b = order[(i + 1) % n]
            if frozenset((a, b)) not in adj:
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Brute-force (DPLL) solver for SAT
# ----------------------------------------------------------------------

def _simplify(clauses, var, val):
    """Assign var=val and simplify; returns the reduced clause list."""
    true_lit = var if val else -var
    false_lit = -var if val else var
    out = []
    for clause in clauses:
        if true_lit in clause:
            continue  # clause satisfied
        new_clause = [lit for lit in clause if lit != false_lit]
        out.append(new_clause)
    return out


def sat_yes(num_vars, clauses):
    clauses = [list(c) for c in clauses]

    def rec(clauses):
        # unit propagation
        while True:
            if any(len(c) == 0 for c in clauses):
                return False
            if not clauses:
                return True
            unit = None
            for c in clauses:
                if len(c) == 1:
                    unit = c[0]
                    break
            if unit is None:
                break
            clauses = _simplify(clauses, abs(unit), unit > 0)
        if not clauses:
            return True
        var = abs(clauses[0][0])
        for val in (True, False):
            if rec(_simplify(clauses, var, val)):
                return True
        return False

    return rec(clauses)


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_graphs(n):
    verts = list(range(n))
    possible = [(u, v) for u in verts for v in verts if u < v]
    for mask in range(1 << len(possible)):
        edges = [list(e) for k, e in enumerate(possible) if (mask >> k) & 1]
        yield {"n": n, "edges": edges}



def random_graph_reversed(n, rng, p=0.5):
    g = random_graph(n, rng, p)
    edges = []
    for u, v in g["edges"]:
        edges.append([v, u] if rng.random() < 0.5 else [u, v])
    return {"n": n, "edges": edges}


def structured_graphs():
    out = []
    # Cycles (Hamiltonian) for various n.
    for n in range(3, 13):
        out.append({"n": n, "edges": [[i, (i + 1) % n] for i in range(n)]})
        # cycle plus a chord
        e = [[i, (i + 1) % n] for i in range(n)]
        if n >= 4:
            e.append([0, 2])
        out.append({"n": n, "edges": e})
    # Complete graphs.
    for n in range(3, 9):
        out.append({"n": n, "edges": [[u, v] for u in range(n) for v in range(u + 1, n)]})
    # Star graphs (never Hamiltonian for n >= 4).
    for n in range(3, 10):
        out.append({"n": n, "edges": [[0, v] for v in range(1, n)]})
    return out


def random_graph(n, rng, p=0.5):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    instances = []
    # Exhaustive over all graphs for n = 0..5.
    for n in range(0, 6):
        instances.extend(all_graphs(n))
    # Random samples for slightly larger n.
    rng = random.Random(12345)
    for n in range(6, 9):
        for _ in range(300):
            instances.append(random_graph(n, rng))
            instances.append(random_graph(n, rng, p=0.8))
            instances.append(random_graph(n, rng, p=0.3))
    # Reversed edge orderings.
    for n in range(3, 8):
        for _ in range(200):
            instances.append(random_graph_reversed(n, rng))
            instances.append(random_graph_reversed(n, rng, p=0.75))
    # Structured larger graphs.
    instances.extend(structured_graphs())

    for inst in instances:
        tests_run += 1
        try:
            HamiltonianCycle.validate(inst)
        except Exception as exc:  # pragma: no cover
            failures.append((inst, f"source instance invalid: {exc}"))
            continue

        expected = hamiltonian_yes(inst["n"], inst["edges"])

        try:
            out = reduce(inst)
        except Exception as exc:
            failures.append((inst, f"reduce raised: {exc!r}"))
            continue

        # The output must be a valid Sat instance.
        try:
            Sat.validate(out)
        except Exception as exc:
            failures.append((inst, f"reduction output invalid: {exc}"))
            continue

        got = sat_yes(out["num_vars"], out["clauses"])

        if got == expected:
            tests_passed += 1
        else:
            failures.append(
                (inst, f"expected {expected}, reduction gives {got}")
            )

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for inst, msg in failures[:20]:
            print("  ", inst, "->", msg)
    else:
        print("ALL TESTS PASSED")

    verified = (tests_run > 0 and tests_passed == tests_run and not failures)
    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
        )
    print("verdict.json:", json.dumps({"verified": verified,
                                        "tests_run": tests_run,
                                        "tests_passed": tests_passed}))
    return 0 if verified else 1


if __name__ == "__main__":
    sys.exit(main())
