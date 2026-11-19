import itertools
import random
import json
from problems import DominatingSet, Sat, InvalidInstance
from reduce import reduce

def dominating_set_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    # edge case handling as per definition
    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True
    # adjacency set
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    vertices = list(range(n))
    for r in range(k+1):
        for subset in itertools.combinations(vertices, r):
            D = set(subset)
            # check domination
            ok = True
            for v in vertices:
                if v not in D and not (adj[v] & D):
                    ok = False
                    break
            if ok:
                return True
    return False

def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # empty clause unsat
    for clause in clauses:
        if len(clause) == 0:
            return False
    # iterate assignments
    for bits in itertools.product([False, True], repeat=m):
        assign = {i+1: bits[i] for i in range(m)}
        sat = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit)
                val = assign[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_sat = True
                    break
            if not clause_sat:
                sat = False
                break
        if sat:
            return True
    return False

def random_instance(max_n=5):
    n = random.randint(0, max_n)
    # generate random edges without duplicates
    possible = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = []
    for (u, v) in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n+1)
    return {"n": n, "edges": edges, "k": k}

tests = 0
passes = 0
for _ in range(200):
    inst = random_instance()
    # validate
    try:
        DominatingSet.validate(inst)
    except InvalidInstance as e:
        continue
    reduced = reduce(inst)
    # validate reduced
    Sat.validate(reduced)
    ds_ans = dominating_set_bruteforce(inst)
    sat_ans = sat_bruteforce(reduced)
    tests += 1
    if ds_ans == sat_ans:
        passes += 1
    else:
        print('Mismatch!')
        print('Inst:', inst)
        print('Reduced:', reduced)
        print('DS:', ds_ans, 'SAT:', sat_ans)
        break

# also test some edge cases explicitly
edge_cases = [
    {"n":0, "edges":[], "k":0},
    {"n":0, "edges":[], "k":-1},
    {"n":3, "edges":[], "k":2},
    {"n":3, "edges":[[0,1],[1,2]], "k":-1},
]
for inst in edge_cases:
    DominatingSet.validate(inst)
    reduced = reduce(inst)
    Sat.validate(reduced)
    ds_ans = dominating_set_bruteforce(inst)
    sat_ans = sat_bruteforce(reduced)
    tests += 1
    if ds_ans == sat_ans:
        passes += 1
    else:
        print('Edge case mismatch')
        print(inst, reduced, ds_ans, sat_ans)
        break

verdict = {
    "verified": passes == tests,
    "tests_run": tests,
    "tests_passed": passes,
}
print(json.dumps(verdict))
with open('verdict.json', 'w') as f:
    json.dump(verdict, f)
