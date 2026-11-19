"""Independent verification of reduce.py (Clique -> SAT).

We implement exact solvers for both problems from the definitions in
problems.py, then compare the source answer with the answer to its reduction
on many small instances.
"""
import itertools
import random

from problems import Clique, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Exact brute-force solvers
# ----------------------------------------------------------------------

def solve_clique(inst):
    """True iff the graph has a clique of size >= k."""
    n = inst["n"]
    edges = inst["edges"]
    k = inst["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for size in range(k, n + 1):
        for comb in itertools.combinations(range(n), size):
            good = True
            for i in range(len(comb)):
                for j in range(i + 1, len(comb)):
                    if not adj[comb[i]][comb[j]]:
                        good = False
                        break
                if not good:
                    break
            if good:
                return True
    return False


def solve_sat(inst):
    """Exact DPLL SAT solver (complete)."""
    clauses = [frozenset(c) for c in inst["clauses"]]

    def rec(clauses, assignment):
        # Simplify clauses under the current assignment.
        new = []
        for cl in clauses:
            satisfied = False
            rem = []
            for lit in cl:
                v = abs(lit)
                val = assignment.get(v)
                if val is None:
                    rem.append(lit)
                elif (lit > 0) == val:
                    satisfied = True
                    break
            if satisfied:
                continue
            if not rem:
                return False  # empty clause -> unsat
            new.append(frozenset(rem))
        if not new:
            return True
        # Unit propagation.
        for cl in new:
            if len(cl) == 1:
                lit = next(iter(cl))
                v = abs(lit)
                val = lit > 0
                if v in assignment and assignment[v] != val:
                    return False
                na = dict(assignment)
                na[v] = val
                return rec(new, na)
        # Branch on a literal.
        lit = next(iter(new[0]))
        v = abs(lit)
        for val in (True, False):
            na = dict(assignment)
            na[v] = val
            if rec(new, na):
                return True
        return False

    return rec(clauses, {})


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_graphs(n):
    """Yield every simple undirected graph on n vertices as an edge list."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if (mask >> i) & 1]
        yield edges


def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            Clique.validate(inst)
        except Exception as exc:  # pragma: no cover
            failures.append(("source invalid", inst, repr(exc)))
            return
        expected = solve_clique(inst)
        try:
            out = reduce(inst)
        except Exception as exc:
            failures.append(("reduce raised", inst, repr(exc)))
            return
        # The output must be a valid SAT instance.
        try:
            Sat.validate(out)
        except Exception as exc:
            failures.append(("target invalid", inst, repr(exc)))
            return
        got = solve_sat(out)
        if got != expected:
            failures.append(("mismatch", inst, f"expected={expected} got={got} out={out}"))
        else:
            tests_passed += 1

    # Exhaustive over all graphs on n = 0..5 and a range of k values.
    for n in range(0, 6):
        ks = list(range(-2, n + 3))
        for edges in all_graphs(n):
            for k in ks:
                check({"n": n, "edges": edges, "k": k})

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 7)
        edges = random_graph(n, rng.random(), rng)
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:20]:
        print("FAIL:", f)

    with open("test_results.txt", "w") as fh:
        fh.write(f"{tests_run} {tests_passed} {len(failures)}\n")
        for f in failures[:20]:
            fh.write(repr(f) + "\n")

    return tests_run, tests_passed, len(failures)


if __name__ == "__main__":
    main()
