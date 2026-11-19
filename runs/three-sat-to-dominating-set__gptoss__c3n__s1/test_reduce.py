import itertools
import random
import sys
from typing import List, Dict

import problems
from reduce import reduce


def solve_three_sat(instance: Dict) -> bool:
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # iterate over all assignments
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            satisfied = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0 and val:
                    satisfied = True
                if lit < 0 and not val:
                    satisfied = True
                if satisfied:
                    break
            if not satisfied:
                ok = False
                break
        if ok:
            return True
    return False


def solve_dominating_set(instance: Dict) -> bool:
    n = instance["n"]
    k = instance["k"]
    edges = instance["edges"]
    # adjacency list including self
    adj = [set([i]) for i in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # try all subsets up to k
    for size in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), size):
            dominated = set()
            for v in subset:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False


def random_three_sat(max_vars=4, max_clauses=5) -> Dict:
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    if m < 3:
        # allow zero clauses only
        clauses = []
    else:
        c = random.randint(0, max_clauses)
        clauses = []
        for _ in range(c):
            # pick 3 distinct vars
            vars = random.sample(range(1, m + 1), 3)
            clause = []
            for v in vars:
                lit = v if random.choice([True, False]) else -v
                clause.append(lit)
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        inst = random_three_sat()
        # validate
        try:
            problems.ThreeSat.validate(inst)
        except Exception as e:
            print("Invalid generated instance", e)
            continue
        sat = solve_three_sat(inst)
        dom_inst = reduce(inst)
        dom = solve_dominating_set(dom_inst)
        # reduction should preserve answer (sat iff dom)
        if sat == dom:
            passed += 1
        else:
            print("Mismatch!", inst, sat, dom_inst, dom)
        total += 1
    # also test edge cases explicitly
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1,2,3]]},
        {"num_vars": 3, "clauses": [[1,-2,3], [-1,2,-3]]},
    ]
    for inst in edge_cases:
        problems.ThreeSat.validate(inst)
        sat = solve_three_sat(inst)
        dom_inst = reduce(inst)
        dom = solve_dominating_set(dom_inst)
        if sat == dom:
            passed += 1
        else:
            print("Mismatch edge", inst, sat, dom_inst, dom)
        total += 1
    print(f"Tests run: {total}, passed: {passed}")
    # write verdict.json
    import json
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    if passed != total:
        sys.exit(1)

if __name__ == "__main__":
    main()
