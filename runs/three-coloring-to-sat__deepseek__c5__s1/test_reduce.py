"""Independent tests for reduce.py: 3-Coloring -> SAT.

We implement our own solvers for both problems directly from the definitions
in problems.py, then compare the source answer with the answer to the reduced
instance on many small instances (exhaustive for tiny graphs, randomized for
larger ones).
"""

import itertools
import random

from problems import ThreeColoring, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the definitions.

def solve_three_coloring(instance):
    """Return True iff the graph is 3-colourable (brute force over colourings)."""
    n = instance["n"]
    edges = instance["edges"]
    for coloring in itertools.product(range(3), repeat=n):
        if all(coloring[u] != coloring[v] for u, v in edges):
            return True
    return False


def solve_sat_bruteforce(instance):
    """Return True iff the CNF formula is satisfiable (exhaustive)."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        def lit_value(lit):
            val = bits[abs(lit) - 1]
            return val if lit > 0 else not val
        if all(any(lit_value(lit) for lit in clause) for clause in clauses):
            return True
    return False


def solve_sat(instance):
    """Return True iff the CNF formula is satisfiable (DPLL + unit propagation)."""
    clauses = [list(c) for c in instance["clauses"]]

    def eval_clause(clause, assignment):
        unknown = False
        for lit in clause:
            v = abs(lit)
            if v in assignment:
                if assignment[v] == (lit > 0):
                    return True
            else:
                unknown = True
        return None if unknown else False

    def dpll(assignment):
        # unit propagation
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                status = eval_clause(clause, assignment)
                if status is False:
                    return False
                if status is None:
                    unassigned = [lit for lit in clause if abs(lit) not in assignment]
                    if len(unassigned) == 1:
                        lit = unassigned[0]
                        assignment[abs(lit)] = (lit > 0)
                        changed = True
        if all(eval_clause(c, assignment) is True for c in clauses):
            return True
        var = None
        for clause in clauses:
            if eval_clause(clause, assignment) is None:
                for lit in clause:
                    if abs(lit) not in assignment:
                        var = abs(lit)
                        break
                break
        if var is None:
            return True
        for value in (True, False):
            new = dict(assignment)
            new[var] = value
            if dpll(new):
                return True
        return False

    return dpll({})


# ----------------------------------------------------------------------
# Instance generators (valid instances only).

def random_graph(rng, n, p):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def all_graphs(n):
    """Yield every simple graph on n labelled vertices (exhaustive)."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Tests.

def check(instance, results, sat_solver=solve_sat):
    ThreeColoring.validate(instance)
    expected = solve_three_coloring(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    got = sat_solver(reduced)
    results["tests_run"] += 1
    if got == expected:
        results["tests_passed"] += 1
    else:
        results["failures"].append((instance, expected, reduced, got))


def main():
    results = {"tests_run": 0, "tests_passed": 0, "failures": []}

    # 0. Cross-check the two SAT solvers on random small formulas.
    rng0 = random.Random(999)
    for _ in range(300):
        m = rng0.randint(0, 6)
        clauses = []
        for _ in range(rng0.randint(0, 5)):
            clauses.append([rng0.choice([-1, 1]) * rng0.randint(1, m) for _ in range(rng0.randint(0, 3))] if m else [])
        f = {"num_vars": m, "clauses": clauses}
        Sat.validate(f)
        assert solve_sat(f) == solve_sat_bruteforce(f), f

    # 1. Exhaustive over all graphs with n = 0..5.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g, results)

    # 2. Explicit edge cases.
    edge_cases = [
        {"n": 0, "edges": []},                       # empty graph: yes
        {"n": 1, "edges": []},                       # yes
        {"n": 2, "edges": [[0, 1]]},                 # yes
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, # triangle: yes
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3],
                            [1, 2], [1, 3], [2, 3]]}, # K4: no
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]},  # C5: no
        {"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]]},  # C6: yes
        {"n": 4, "edges": []},                       # edgeless: yes
    ]
    for g in edge_cases:
        check(g, results)

    # 3. Randomized larger graphs.
    rng = random.Random(12345)
    for _ in range(500):
        n = rng.randint(0, 12)
        p = rng.choice([0.0, 0.15, 0.3, 0.5, 0.8, 1.0])
        g = random_graph(rng, n, p)
        check(g, results)

    # 4. Random K4-containing graphs (should be unsatisfiable).
    for _ in range(200):
        n = rng.randint(4, 12)
        verts = rng.sample(range(n), 4)
        edges = [[verts[i], verts[j]] for i in range(4) for j in range(i + 1, 4)]
        existing = {frozenset(e) for e in edges}
        for u in range(n):
            for v in range(u + 1, n):
                if frozenset((u, v)) not in existing and rng.random() < 0.3:
                    edges.append([u, v])
        check({"n": n, "edges": edges}, results)

    # 5. Odd cycles (unsatisfiable) and even cycles (satisfiable).
    for k in range(3, 15):
        edges = [[i, (i + 1) % k] for i in range(k)]
        check({"n": k, "edges": edges}, results)

    # 6. Complete graphs K_n: K1..K3 yes, K4+ no.
    for n in range(0, 9):
        edges = [[u, v] for u in range(n) for v in range(u + 1, n)]
        check({"n": n, "edges": edges}, results)

    # 7. Bipartite-ish graphs (always 3-colourable).
    for _ in range(200):
        n = rng.randint(0, 14)
        edges = []
        for u in range(n):
            for v in range(u + 1, n):
                if (u % 2) != (v % 2) and rng.random() < 0.5:
                    edges.append([u, v])
        check({"n": n, "edges": edges}, results)

    print(f"tests_run={results['tests_run']} tests_passed={results['tests_passed']}")
    for inst, expected, reduced, got in results["failures"][:10]:
        print("FAILURE:", inst, "expected", expected, "got", got)
    return results


if __name__ == "__main__":
    r = main()
    assert not r["failures"], "there were failures"
    print("ALL TESTS PASSED")
