import itertools
import random
import json
from problems import ThreeColoring, OneInThreeSat
from reduce import reduce

def three_coloring_solver(instance):
    n = instance['n']
    edges = instance['edges']
    for coloring in itertools.product(range(3), repeat=n):
        if all(coloring[u] != coloring[v] for u, v in edges):
            return True
    return False

def one_in_three_sat_solver(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for assign in itertools.product([False, True], repeat=m):
        if all(sum(assign[l-1] for l in clause) == 1 for clause in clauses):
            return True
    return False

def generate_random_graph(max_n=4, edge_prob=0.3):
    """Generate a small random graph for exhaustive testing."""
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {"n": n, "edges": edges}

random.seed(0)

tests = 0
passed = 0
for _ in range(200):
    g = generate_random_graph()
    ThreeColoring.validate(g)
    red = reduce(g)
    OneInThreeSat.validate(red)
    # Skip large reductions to keep exhaustive SAT solver tractable
    if red["num_vars"] > 20:
        continue
    src = three_coloring_solver(g)
    tgt = one_in_three_sat_solver(red)
    tests += 1
    if src == tgt:
        passed += 1
    else:
        print('Mismatch!')
        print('Graph:', json.dumps(g))
        print('Reduced:', json.dumps(red))
        print('src', src, 'tgt', tgt)
        break

# Edge cases
edge_cases = [
    {"n": 0, "edges": []},
    {"n": 1, "edges": []},
    {"n": 2, "edges": []},
    {"n": 3, "edges": []},
    {"n": 4, "edges": [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]}, # K4
]
for g in edge_cases:
    ThreeColoring.validate(g)
    red = reduce(g)
    OneInThreeSat.validate(red)
    if red["num_vars"] > 20:
        continue
    src = three_coloring_solver(g)
    tgt = one_in_three_sat_solver(red)
    tests += 1
    if src == tgt:
        passed += 1
    else:
        print('Edge case mismatch', g)
        break

verdict = {"verified": passed == tests, "tests_run": tests, "tests_passed": passed}
with open('verdict.json', 'w') as f:
    json.dump(verdict, f)
print('Done', verdict)
