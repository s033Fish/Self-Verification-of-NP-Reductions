import itertools
import json
import random
import sys
from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce

def is_hamiltonian_cycle(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n <= 2:
        return False
    # generate permutations of vertices starting with 0 to avoid rotations
    for perm in itertools.permutations(range(n)):
        # check cycle edges
        ok = True
        for i in range(n):
            u = perm[i]
            v = perm[(i+1)%n]
            if frozenset((u,v)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def is_hamiltonian_path(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        return frozenset((0,1)) in edges
    # for n>=3, try all permutations
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n-1):
            if frozenset((perm[i], perm[i+1])) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

# generate all graphs up to n=5
max_n = 5
tests = 0
passed = 0
for n in range(max_n+1):
    vertices = list(range(n))
    possible_edges = [(u,v) for u in vertices for v in vertices if u < v]
    # iterate over subsets, but limit number for n=5 (2^10=1024 manageable)
    for mask in range(1 << len(possible_edges)):
        edges = []
        for i, e in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append([e[0], e[1]])
        instance = {"n": n, "edges": edges}
        # validate
        try:
            HamiltonianCycle.validate(instance)
            HamiltonianPath.validate(instance)
        except Exception as e:
            print("Invalid instance", e)
            sys.exit(1)
        src = is_hamiltonian_cycle(instance)
        reduced = reduce(instance)
        tgt = is_hamiltonian_path(reduced)
        tests += 1
        if src == tgt:
            passed += 1
        else:
            print("Mismatch! n", n, "edges", edges, "src", src, "tgt", tgt)
            sys.exit(1)
print(f"All {tests} tests passed: {passed} == {tests}")
