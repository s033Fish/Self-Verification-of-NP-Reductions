import itertools
import random
import json
from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce

def is_hamiltonian_path(instance):
    n = instance['n']
    edges = set()
    for u, v in instance['edges']:
        edges.add(frozenset((u, v)))
    if n == 0:
        return False
    if n == 1:
        return True
    # generate all permutations of vertices
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n-1):
            if frozenset((perm[i], perm[i+1])) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def is_hamiltonian_cycle(instance):
    n = instance['n']
    edges = set(frozenset((u, v)) for u, v in instance['edges'])
    if n <= 2:
        return False
    # permutations of vertices fixing start=0 to avoid rotations
    verts = list(range(n))
    for perm in itertools.permutations(verts[1:]):
        cycle = (0,) + perm
        ok = True
        for i in range(n):
            u = cycle[i]
            v = cycle[(i+1)%n]
            if frozenset((u, v)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def random_graph(n, p=0.5):
    edges = []
    for i in range(n):
        for j in range(i+1, n):
            if random.random() < p:
                edges.append([i, j])
    return {'n': n, 'edges': edges}

def test_one(instance):
    # validate
    HamiltonianPath.validate(instance)
    red = reduce(instance)
    HamiltonianCycle.validate(red)
    ans_path = is_hamiltonian_path(instance)
    ans_cycle = is_hamiltonian_cycle(red)
    if ans_path != ans_cycle:
        print('Mismatch!')
        print('orig', instance)
        print('reduced', red)
        print('path', ans_path, 'cycle', ans_cycle)
        return False
    return True

random.seed(0)
tests = 0
passed = 0
# test all graphs up to n=5
for n in range(0,6):
    # enumerate all possible edge sets for n up to 4 maybe, else random
    max_edges = n*(n-1)//2
    if max_edges <= 6:
        for mask in range(1<<max_edges):
            edges = []
            idx = 0
            for i in range(n):
                for j in range(i+1, n):
                    if mask & (1<<idx):
                        edges.append([i,j])
                    idx+=1
            instance = {'n': n, 'edges': edges}
            tests+=1
            if test_one(instance):
                passed+=1
    else:
        for _ in range(200):
            instance = random_graph(n, p=0.5)
            tests+=1
            if test_one(instance):
                passed+=1
print('Tests run:', tests, 'passed:', passed)
# write verdict
verdict = {'verified': tests==passed, 'tests_run': tests, 'tests_passed': passed}
with open('verdict.json','w') as f:
    json.dump(verdict, f)
