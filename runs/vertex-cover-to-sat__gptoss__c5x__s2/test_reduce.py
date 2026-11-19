"""Independent tests for reduce.py (Vertex Cover -> SAT).

We implement brute-force solvers for both problems from the definitions in
problems.py, then compare the answers on many small source instances and
their reductions.
"""
import itertools
import json

from problems import VertexCover, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the definitions)
# ----------------------------------------------------------------------

def solve_vertex_cover(instance):
    """Return True iff graph has a vertex cover of size AT MOST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True  # all vertices cover every edge
    vertices = range(n)
    for size in range(0, k + 1):
        for subset in itertools.combinations(vertices, size):
            s = set(subset)
            if all(u in s or v in s for u, v in edges):
                return True
    return False


def solve_sat(instance):
    """Return True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # variable v (1..m) is bits[v-1]
        ok = True
        for clause in clauses:
            if not any((bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                       for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_graphs(n):
    """All simple graphs on n vertices (as edge lists)."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield edges


def source_instances():
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                yield {"n": n, "edges": edges, "k": k}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    for inst in source_instances():
        tests_run += 1
        VertexCover.validate(inst)
        expected = solve_vertex_cover(inst)
        reduced = reduce(inst)
        Sat.validate(reduced)
        got = solve_sat(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((inst, expected, reduced, got))

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:20]:
        print("FAIL:", f)

    verdict = {
        "verified": len(failures) == 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
