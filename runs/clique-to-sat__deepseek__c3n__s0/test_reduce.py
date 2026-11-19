"""Tests for reduce.py: brute-force solvers for Clique and SAT, compared
on many small instances."""

from __future__ import annotations

import itertools
import random

from reduce import reduce
import problems


# ---------------------------------------------------------------- solvers


def clique_solve(instance: dict) -> bool:
    """Brute force: does the graph have a clique of size >= k?"""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k <= 0:
        return True
    if k > n:
        return False

    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True

    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(adj[u][v] for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def sat_solve(instance: dict) -> bool:
    """Self-written DPLL solver: is the CNF formula satisfiable?"""
    m = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        # assignment: dict var -> bool
        while True:
            # Simplify clauses under current assignment.
            simplified = []
            unit = None
            for clause in clauses:
                new_clause = []
                satisfied = False
                for lit in clause:
                    v = abs(lit)
                    if v in assignment:
                        if assignment[v] == (lit > 0):
                            satisfied = True
                            break
                    else:
                        new_clause.append(lit)
                if satisfied:
                    continue
                if not new_clause:
                    return False  # empty clause -> unsatisfiable
                simplified.append(new_clause)
                if len(new_clause) == 1:
                    unit = new_clause[0]
            clauses = simplified
            if unit is None:
                break
            assignment = dict(assignment)
            assignment[abs(unit)] = unit > 0
        if not clauses:
            return True
        # Choose the variable occurring most often.
        counts = {}
        for clause in clauses:
            for lit in clause:
                counts[abs(lit)] = counts.get(abs(lit), 0) + 1
        var = max(counts, key=counts.get)
        for value in (True, False):
            new_assignment = dict(assignment)
            new_assignment[var] = value
            if dpll(clauses, new_assignment):
                return True
        return False

    return dpll(clauses, {})


# ---------------------------------------------------------------- helpers


def all_graphs(n: int):
    """Yield all simple graphs on n vertices as edge lists."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for idx, p in enumerate(pairs) if (mask >> idx) & 1]
        yield edges


def check(instance: dict, counter: list) -> None:
    problems.Clique.validate(instance)
    out = reduce(instance)
    problems.Sat.validate(out)
    expected = clique_solve(instance)
    got = sat_solve(out)
    counter[0] += 1
    assert got == expected, (
        f"mismatch on {instance}: clique={expected}, sat={got}, out={out}"
    )
    if expected:
        counter[1] += 1


def main() -> None:
    counter = [0, 0]  # [tests, yes_answers]

    # Exhaustive small graphs, k from -2 to n+2.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k}, counter)

    # A few larger exhaustive-ish random graphs.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 7)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        k = rng.randint(-1, n + 2)
        check({"n": n, "edges": edges, "k": k}, counter)

    # Dense graphs (cliques likely) to exercise the yes side.
    for _ in range(200):
        n = rng.randint(1, 7)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.85]
        k = rng.randint(1, n)
        check({"n": n, "edges": edges, "k": k}, counter)

    # Sparse graphs (cliques unlikely).
    for _ in range(200):
        n = rng.randint(1, 7)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.2]
        k = rng.randint(1, n)
        check({"n": n, "edges": edges, "k": k}, counter)

    print(f"tests_run={counter[0]} tests_passed={counter[0]} "
          f"(yes answers={counter[1]})")


if __name__ == "__main__":
    main()
