import itertools
import random
from typing import List, Dict

from problems import ThreeSat, DominatingSet
from reduce import reduce


def solve_three_sat(instance: Dict) -> bool:
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # iterate over all assignments
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1  # 1 = True
                if lit > 0 and val == 1:
                    clause_ok = True
                    break
                if lit < 0 and val == 0:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_dominating_set(instance: Dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    # build adjacency list
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # a vertex dominates itself and its neighbors
    all_vertices = set(range(n))
    # try all subsets up to size k (if k >= n trivial yes)
    if k >= n:
        return True
    for r in range(k + 1):
        for subset in itertools.combinations(range(n), r):
            dominated = set(subset)
            for v in subset:
                dominated.update(adj[v])
            if dominated == all_vertices:
                return True
    return False


def generate_all_three_sat_instances(max_vars=3, max_clauses=3):
    instances = []
    for m in range(max_vars + 1):
        # generate all possible literals for variables 1..m
        literals = []
        for var in range(1, m + 1):
            literals.append(var)
            literals.append(-var)
        # generate all possible clauses (choose 3 distinct vars)
        var_combos = list(itertools.combinations(range(1, m + 1), 3))
        clause_options = []
        for combo in var_combos:
            # for each variable choose sign +/-
            for signs in itertools.product([1, -1], repeat=3):
                clause = [signs[i] * combo[i] for i in range(3)]
                clause_options.append(clause)
        # also allow empty clause list
        clause_lists = [[]]
        for r in range(1, max_clauses + 1):
            for combo in itertools.combinations(clause_options, r):
                clause_lists.append([list(c) for c in combo])
        for clauses in clause_lists:
            instance = {"num_vars": m, "clauses": clauses}
            instances.append(instance)
    return instances


def main():
    random.seed(0)
    instances = generate_all_three_sat_instances(max_vars=3, max_clauses=2)
    total = len(instances)
    passed = 0
    for inst in instances:
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        DominatingSet.validate(reduced)
        sat = solve_three_sat(inst)
        dom = solve_dominating_set(reduced)
        if sat == dom:
            passed += 1
        else:
            print("Mismatch!", inst, reduced, sat, dom)
            break
    print(f"{passed}/{total} tests passed")
    # write verdict
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    import json, sys
    json.dump(verdict, open('verdict.json', 'w'))
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
