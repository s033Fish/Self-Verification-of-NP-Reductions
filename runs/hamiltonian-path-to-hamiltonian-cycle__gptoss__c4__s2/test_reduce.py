import itertools
import json
from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce

def is_hamiltonian_path(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        return frozenset((0,1)) in edges
    # brute force permutations
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
    edges = set(frozenset(e) for e in instance['edges'])
    if n <= 2:
        return False
    if n == 3:
        # triangle required
        return all(frozenset((i,j)) in edges for i,j in [(0,1),(1,2),(2,0)])
    # brute force cycles: fix start at 0 to avoid rotations
    vertices = list(range(n))
    for perm in itertools.permutations(vertices[1:]):
        cycle = (0,)+perm
        ok = True
        for i in range(n):
            u = cycle[i]
            v = cycle[(i+1)%n]
            if frozenset((u,v)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def all_graphs(n):
    verts = list(range(n))
    possible_edges = list(itertools.combinations(verts, 2))
    for mask in range(1<<len(possible_edges)):
        edges = []
        for i, e in enumerate(possible_edges):
            if mask & (1<<i):
                edges.append([e[0], e[1]])
        yield {"n": n, "edges": edges}


tests_run = 0
tests_passed = 0
for n in range(0,5):
    for G in all_graphs(n):
        # validate source
        HamiltonianPath.validate(G)
        path_yes = is_hamiltonian_path(G)
        G2 = reduce(G)
        HamiltonianCycle.validate(G2)
        cycle_yes = is_hamiltonian_cycle(G2)
        tests_run += 1
        if path_yes == cycle_yes:
            tests_passed += 1
        else:
            print("Mismatch!", G, "=>", G2, path_yes, cycle_yes)

verdict = {
    "verified": tests_run == tests_passed,
    "tests_run": tests_run,
    "tests_passed": tests_passed,
}
with open('verdict.json', 'w') as f:
    json.dump(verdict, f)
print(json.dumps(verdict))
