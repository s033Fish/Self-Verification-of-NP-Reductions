import random
import itertools
import sys
from typing import List, Dict, Any

# Import the reduction and problem definitions
from reduce import reduce as reduction
from problems import Clique, Sat

# Brute-force solver for Clique
def solve_clique(instance: Dict[str, Any]) -> bool:
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    k = instance["k"]
    # Edge cases
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # Check all subsets of size k or larger
    for size in range(k, n+1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False

# Brute-force solver for SAT (CNF)
def solve_sat(instance: Dict[str, Any]) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge case: empty clause list => satisfiable
    # empty clause => unsatisfiable
    # We'll just brute force all assignments
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # clause satisfied if any literal true
            sat_clause = False
            for lit in clause:
                var = abs(lit) - 1
                if var < 0 or var >= m:
                    raise ValueError("Invalid literal")
                val = assign[var]
                if lit > 0 and val:
                    sat_clause = True
                    break
                if lit < 0 and not val:
                    sat_clause = True
                    break
            if not sat_clause:
                ok = False
                break
        if ok:
            return True
    return False

def random_graph(max_n: int) -> Dict[str, Any]:
    n = random.randint(0, max_n)
    possible = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = []
    for u, v in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n+2)  # allow some out of range values
    return {"n": n, "edges": edges, "k": k}

def main():
    random.seed(0)
    tests = 200
    passed = 0
    for _ in range(tests):
        inst = random_graph(5)  # small for brute force
        # validate
        try:
            Clique.validate(inst)
        except Exception as e:
            # invalid instance generated, skip
            continue
        reduced = reduction(inst)
        # validate reduced
        Sat.validate(reduced)
        ans_src = solve_clique(inst)
        ans_tgt = solve_sat(reduced)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", inst, reduced, ans_src, ans_tgt, file=sys.stderr)
            sys.exit(1)
    print({"verified": True, "tests_run": tests, "tests_passed": passed})

if __name__ == "__main__":
    main()
