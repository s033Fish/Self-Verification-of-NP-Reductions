import itertools
import json
import random
import sys
from typing import List, Dict

import problems
from problems import ThreeSat, DominatingSet
import reduce


def solve_three_sat(instance: Dict) -> bool:
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
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
    DominatingSet.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if n == 0:
        return k >= 0
    # adjacency list including self
    adj = [set([i]) for i in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # try all subsets of size up to k (but limit to reasonable size)
    # if k >= n, always yes
    if k >= n:
        return True
    for size in range(k + 1):
        for subset in itertools.combinations(range(n), size):
            dominated = set()
            for v in subset:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False


def random_three_sat(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if clauses present
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct vars from 1..max(m,3)
        if m < 3:
            # cannot have clause, break
            break
        vars = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    random.seed(0)
    tests = 200
    passed = 0
    for _ in range(tests):
        inst = random_three_sat()
        three_sat_ans = solve_three_sat(inst)
        dom_inst = reduce.reduce(inst)
        dom_ans = solve_dominating_set(dom_inst)
        # reduction expects dom_ans == three_sat_ans (since k=m)
        if dom_ans == three_sat_ans:
            passed += 1
        else:
            print("FAIL", inst, three_sat_ans, dom_inst, dom_ans)
            break
    print(f"{passed}/{tests} tests passed")
    # write verdict
    verdict = {"verified": passed == tests, "tests_run": tests, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
