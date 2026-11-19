import random
import itertools
import json
import sys
from problems import ThreeSat, DominatingSet
from reduce import reduce

def solve_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1  # 1 means true
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

def solve_dominating_set(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    # build adjacency list including self
    adj = [set([i]) for i in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # check all subsets up to k (or all if k>=n)
    max_size = min(k, n)
    for size in range(max_size + 1):
        for combo in itertools.combinations(range(n), size):
            dominated = set()
            for v in combo:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False

def random_three_sat(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure if clauses >0 then m>=3 per spec, but we can still generate.
    if m < 3:
        # allow zero clauses only
        clauses = []
    else:
        num_clauses = random.randint(0, max_clauses)
        clauses = []
        for _ in range(num_clauses):
            vars_chosen = random.sample(range(1, m+1), 3)
            clause = []
            for v in vars_chosen:
                lit = v if random.choice([True, False]) else -v
                clause.append(lit)
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        inst = random_three_sat()
        # validate
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        DominatingSet.validate(reduced)
        ans1 = solve_three_sat(inst)
        ans2 = solve_dominating_set(reduced)
        if ans1 == ans2:
            passed += 1
        else:
            print('Mismatch!')
            print('3SAT:', json.dumps(inst))
            print('Reduced:', json.dumps(reduced))
            print('3SAT ans', ans1, 'Dom ans', ans2)
            sys.exit(1)
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_tests()
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
