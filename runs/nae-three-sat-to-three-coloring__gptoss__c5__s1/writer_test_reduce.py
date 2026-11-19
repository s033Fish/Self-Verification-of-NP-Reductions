import itertools
import random
import json
from typing import List, Dict, Any

from problems import NaeThreeSat, ThreeColoring
from reduce import reduce


def solve_naesat_bruteforce(instance: Dict[str, Any]) -> bool:
    NaeThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            vals = []
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit < 0:
                    val = not val
                vals.append(val)
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_coloring_bruteforce(instance: Dict[str, Any]) -> bool:
    ThreeColoring.validate(instance)
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    colors = [0, 1, 2]
    for assignment in itertools.product(colors, repeat=n):
        good = True
        for u, v in edges:
            if assignment[u] == assignment[v]:
                good = False
                break
        if good:
            return True
    return False


def random_naesat_instance(max_vars=3, max_clauses=1) -> Dict[str, Any]:
    """Generate a tiny random NAE‑3‑SAT instance for quick testing."""
    m = random.randint(0, max_vars)
    if m < 3:
        clauses: List[List[int]] = []
    else:
        num_clauses = random.randint(0, max_clauses)
        clauses = []
        for _ in range(num_clauses):
            vars_in_clause = random.sample(range(1, m + 1), 3)
            clause = []
            for v in vars_in_clause:
                lit = v if random.choice([True, False]) else -v
                clause.append(lit)
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=100):
    passed = 0
    for i in range(num_tests):
        inst = random_naesat_instance()
        red = reduce(inst)
        ans_src = solve_naesat_bruteforce(inst)
        ans_tgt = solve_three_coloring_bruteforce(red)
        if ans_src != ans_tgt:
            print("Mismatch on test", i)
            print("source", json.dumps(inst))
            print("reduced", json.dumps(red))
            print("src ans", ans_src, "tgt ans", ans_tgt)
            return False, i + 1
        passed += 1
    return True, passed

if __name__ == "__main__":
    ok, count = run_tests()
    print("All tests passed?", ok, "tests run", count)
