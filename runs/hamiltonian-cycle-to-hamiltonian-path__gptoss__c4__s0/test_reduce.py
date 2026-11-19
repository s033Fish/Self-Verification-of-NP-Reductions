import itertools
import random
import json
import sys
from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce

def is_hamiltonian_cycle(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n <= 2:
        return False
    # check all permutations starting with 0 to avoid duplicates
    for perm in itertools.permutations(range(n)):
        # need cycle: edges between consecutive and last->first
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
    # try all permutations, no need to wrap around
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n-1):
            if frozenset((perm[i], perm[i+1])) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def generate_all_graphs(n):
    verts = list(range(n))
    possible_edges = [list(e) for e in itertools.combinations(verts, 2)]
    for mask in range(1 << len(possible_edges)):
        edges = []
        for i, e in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append(e)
        yield {"n": n, "edges": edges}

def test_random():
    for n in range(0,5):
        for instance in generate_all_graphs(n):
            # validate input
            try:
                HamiltonianCycle.validate(instance)
            except Exception as e:
                print("Invalid source instance", instance, e)
                return False
            reduced = reduce(instance)
            # validate reduced instance
            try:
                HamiltonianPath.validate(reduced)
            except Exception as e:
                print("Invalid reduced instance", reduced, e)
                return False
            src_ans = is_hamiltonian_cycle(instance)
            tgt_ans = is_hamiltonian_path(reduced)
            if src_ans != tgt_ans:
                print("Mismatch!", instance, "=>", reduced, src_ans, tgt_ans)
                return False
    return True

if __name__ == "__main__":
    ok = test_random()
    print("All tests passed" if ok else "Tests failed")
    sys.exit(0 if ok else 1)
