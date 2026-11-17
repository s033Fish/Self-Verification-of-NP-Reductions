"""Brute-force / backtracking solvers and tests comparing 3-Coloring with
its reduction to 1-in-3-SAT."""

from __future__ import annotations

import itertools
import json
import random
import sys

from problems import ThreeColoring, OneInThreeSat
from reduce import reduce

sys.setrecursionlimit(10000)


# ----------------------------------------------------------------------
# Solvers written directly from the problem definitions.

def solve_three_coloring(instance: dict) -> bool:
    """True iff the graph is 3-colourable (try all 3^n colourings)."""
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        if all(colouring[u] != colouring[v] for u, v in edges):
            return True
    return False


def solve_one_in_three_sat(instance: dict) -> bool:
    """Complete solver for positive 1-in-3-SAT.

    Backtracking with 1-in-3 propagation:
      * a clause with >1 true literal is a conflict;
      * a clause with exactly 1 true literal forces all other literals false;
      * a clause with 0 true and 1 unassigned literal forces it true;
      * a clause with 0 true and 0 unassigned literals is a conflict.
    """
    m = instance["num_vars"]
    clauses = [[a - 1 for a in clause] for clause in instance["clauses"]]
    if not clauses:
        return True

    def propagate(assign: dict) -> bool:
        """Propagate; return False on conflict. Mutates assign."""
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                vals = [assign.get(v) for v in clause]
                true_count = sum(1 for x in vals if x is True)
                unassigned = [v for v, x in zip(clause, vals) if x is None]
                if true_count > 1:
                    return False
                if true_count == 1:
                    for v in unassigned:
                        assign[v] = False
                        changed = True
                elif not unassigned:
                    return False
                elif len(unassigned) == 1:
                    assign[unassigned[0]] = True
                    changed = True
        return True

    def search(assign: dict) -> bool:
        if not propagate(assign):
            return False
        # Pick an unassigned variable that occurs in some clause.
        branch_var = None
        for clause in clauses:
            for v in clause:
                if v not in assign:
                    branch_var = v
                    break
            if branch_var is not None:
                break
        if branch_var is None:
            return True  # every clause already has exactly one true literal
        for value in (True, False):
            trial = dict(assign)
            trial[branch_var] = value
            if search(trial):
                return True
        return False

    return search({})


# ----------------------------------------------------------------------
# Instance generators.

def all_graphs(n: int):
    """All simple graphs on n labelled vertices."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random) -> dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(source: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeColoring.validate(source)
        target = reduce(source)
        OneInThreeSat.validate(target)
        expected = solve_three_coloring(source)
        got = solve_one_in_three_sat(target)
        assert got == expected, (
            f"mismatch on {source}: expected {expected}, got {got}, "
            f"reduced to {target}"
        )
        tests_passed += 1

    # Exhaustive over all graphs on 0..5 vertices (covers K4, empty graphs,
    # graphs with isolated vertices, etc.).
    for n in range(0, 6):
        for graph in all_graphs(n):
            check(graph)

    # Random larger graphs.
    rng = random.Random(12345)
    for _ in range(500):
        n = rng.randint(0, 12)
        p = rng.choice([0.0, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0])
        check(random_graph(n, p, rng))

    # Sanity checks on the brute-force solvers against documented edge cases.
    assert solve_three_coloring({"n": 0, "edges": []}) is True
    assert solve_three_coloring({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}) is True
    assert (
        solve_three_coloring(
            {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}
        )
        is False
    )
    assert solve_one_in_three_sat({"num_vars": 0, "clauses": []}) is True
    assert solve_one_in_three_sat({"num_vars": 3, "clauses": [[1, 2, 3]]}) is True
    assert (
        solve_one_in_three_sat({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
        is True
    )
    # Positive 1-in-3-SAT: all four triples over 4 vars -> exactly one true
    # overall can satisfy at most ... it is unsatisfiable.
    unsat = {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]}
    assert solve_one_in_three_sat(unsat) is False
    # A satisfiable non-trivial formula.
    sat = {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}
    assert solve_one_in_three_sat(sat) is True

    # Verify the reduction is polynomial-sized (linear here).
    big = random_graph(50, 0.5, rng)
    out = reduce(big)
    assert out["num_vars"] == 3 * 50 + 3 * len(big["edges"])
    assert len(out["clauses"]) == 50 + 3 * len(big["edges"])

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": True, "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
        )


if __name__ == "__main__":
    main()
