import itertools
import random
import json
from typing import List, Dict, Any

from problems import ThreeSat, DominatingSet
from reduce import reduce


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        assignment = {i + 1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit)
                val = assignment[var]
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def dominating_bruteforce(instance: Dict[str, Any]) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    # adjacency list including self
    adj = [set([i]) for i in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    if k >= n:
        return True
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            dominated = set()
            for v in subset:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False


def random_three_sat(max_vars: int = 4, max_clauses: int = 5) -> Dict[str, Any]:
    """Generate a random 3‑SAT instance respecting the problem constraints.

    The generator ensures that if there are any clauses then ``num_vars`` is at
    least 3, as required by the specification.  When ``num_vars`` is 0 the
    formula must have zero clauses.
    """
    m = random.randint(0, max_vars)
    # If we will generate clauses we need at least 3 variables.
    if m != 0 and m < 3:
        m = 3
    # Decide number of clauses.  If m == 0 we must have 0 clauses.
    if m == 0:
        num_clauses = 0
    else:
        num_clauses = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        vars = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests: int = 200) -> Dict[str, int]:
    passed = 0
    for _ in range(num_tests):
        inst = random_three_sat()
        ThreeSat.validate(inst)
        sat_ans = sat_bruteforce(inst)
        dom_inst = reduce(inst)
        DominatingSet.validate(dom_inst)
        dom_ans = dominating_bruteforce(dom_inst)
        if sat_ans == dom_ans:
            passed += 1
        else:
            print("Mismatch!", inst, sat_ans, dom_ans)
            break
    return {"tests_run": num_tests, "tests_passed": passed, "verified": passed == num_tests}

if __name__ == "__main__":
    result = run_tests(200)
    with open("verdict.json", "w") as f:
        json.dump(result, f)
    print(result)
