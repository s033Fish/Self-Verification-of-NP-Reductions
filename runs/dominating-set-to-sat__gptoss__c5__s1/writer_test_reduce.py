import itertools
import random
import json
from problems import DominatingSet, Sat, InvalidInstance
from reduce import reduce

def solve_dominating(instance):
    DominatingSet.validate(instance)
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True
    # build adjacency sets
    neigh = [set() for _ in range(n)]
    for u, v in edges:
        neigh[u].add(v)
        neigh[v].add(u)
    for i in range(n):
        neigh[i].add(i)
    vertices = list(range(n))
    for size in range(k+1):
        for combo in itertools.combinations(vertices, size):
            dom = set()
            for v in combo:
                dom.update(neigh[v])
            if len(dom) == n:
                return True
    return False

def solve_sat(instance):
    Sat.validate(instance)
    m = instance['num_vars']
    clauses = instance['clauses']
    # quick checks for empty clause
    for cl in clauses:
        if len(cl) == 0:
            return False
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for cl in clauses:
            clause_sat = False
            for lit in cl:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False

def random_instance(max_n=5):
    n = random.randint(0, max_n)
    # generate random edges without duplicates
    possible = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = []
    for (u, v) in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n+2)
    return {"n": n, "edges": edges, "k": k}

def main():
    random.seed(0)
    tests = 200
    passed = 0
    for _ in range(tests):
        inst = random_instance()
        ds_ans = solve_dominating(inst)
        sat_inst = reduce(inst)
        sat_ans = solve_sat(sat_inst)
        if ds_ans == sat_ans:
            passed += 1
        else:
            print('FAIL')
            print('Dominating instance:', json.dumps(inst))
            print('Reduced SAT:', json.dumps(sat_inst))
            print('Dom answer', ds_ans, 'Sat answer', sat_ans)
            break
    # Edge cases explicit
    edge_cases = [
        {"n":0,"edges":[],"k":-1},
        {"n":0,"edges":[],"k":0},
        {"n":0,"edges":[],"k":5},
        {"n":3,"edges":[],"k":2}, # isolated vertices need themselves, impossible size 2 < 3
        {"n":3,"edges":[],"k":3},
    ]
    for ec in edge_cases:
        ds_ans = solve_dominating(ec)
        sat_inst = reduce(ec)
        sat_ans = solve_sat(sat_inst)
        if ds_ans != sat_ans:
            print('EDGE FAIL', ec, ds_ans, sat_ans)
            break
        else:
            passed += 1
    total = tests + len(edge_cases)
    print('Tests run:', total, 'Passed:', passed)
    verdict = {"verified": passed==total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json','w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
