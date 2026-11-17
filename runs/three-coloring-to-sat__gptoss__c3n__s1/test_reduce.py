import itertools
import random
import json
from typing import Dict, Any, List

from problems import ThreeColoring, Sat
from reduce import reduce


def solve_three_coloring(instance: Dict[str, Any]) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    # Edge cases: n=0 always yes, n<=3 always yes (as per definition)
    if n == 0:
        return True
    if n <= 3:
        return True
    # brute force over 3^n assignments
    for colors in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colors[u] == colors[v]:
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat(instance: Dict[str, Any]) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge case: empty clause list -> satisfiable
    # empty clause [] -> unsatisfiable
    for assign in itertools.product([False, True], repeat=m):
        assignment = [None] + list(assign)  # 1-indexed
        all_sat = True
        for clause in clauses:
            # empty clause is always false
            if not clause:
                all_sat = False
                break
            clause_sat = False
            for lit in clause:
                var = abs(lit)
                val = assignment[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                all_sat = False
                break
        if all_sat:
            return True
    return False


def random_graph(max_n=5, edge_prob=0.4) -> Dict[str, Any]:
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        g = random_graph()
        # validate source
        ThreeColoring.validate(g)
        sat = reduce(g)
        Sat.validate(sat)
        ans1 = solve_three_coloring(g)
        ans2 = solve_sat(sat)
        if ans1 == ans2:
            passed += 1
        else:
            print("Mismatch!", g, sat, ans1, ans2)
            break
    return passed, num_trials

if __name__ == "__main__":
    passed, total = run_tests()
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
