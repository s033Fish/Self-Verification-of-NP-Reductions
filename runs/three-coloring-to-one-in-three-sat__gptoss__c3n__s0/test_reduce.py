import itertools
import random
import sys

from problems import ThreeColoring, OneInThreeSat
from reduce import reduce


def solve_three_coloring(instance):
    n = instance["n"]
    edges = instance["edges"]
    # brute force all 3^n colorings
    for colors in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colors[u] == colors[v]:
                ok = False
                break
        if ok:
            return True
    return False


def solve_one_in_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assignment in itertools.product([0, 1], repeat=m):
        good = True
        for clause in clauses:
            true_cnt = sum(assignment[abs(lit)-1] for lit in clause)
            if true_cnt != 1:
                good = False
                break
        if good:
            return True
    return False


def random_graph(max_n=4, edge_prob=0.3):
    """Generate a small random graph.

    The brute‑force solvers used in the tests are exponential, so we keep the
    graph tiny (at most 4 vertices) and relatively sparse.  This is sufficient
    to exercise the reduction while staying well within the time limit.
    """
    n = random.randint(0, max_n)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < edge_prob:
                edges.append([i, j])
    return {"n": n, "edges": edges}


def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        g = random_graph()
        # validate source
        ThreeColoring.validate(g)
        src_ans = solve_three_coloring(g)
        red = reduce(g)
        OneInThreeSat.validate(red)
        tgt_ans = solve_one_in_three_sat(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", g, src_ans, tgt_ans)
            return False, passed
    return True, passed

if __name__ == "__main__":
    ok, passed = run_tests()
    print(f"Tests passed: {passed}")
    sys.exit(0 if ok else 1)
