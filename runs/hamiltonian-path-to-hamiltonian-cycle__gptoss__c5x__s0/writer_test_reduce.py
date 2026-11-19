import itertools
import json
from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce

def is_hamiltonian_path(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        return frozenset((0,1)) in edges
    # check all permutations
    for perm in itertools.permutations(range(n)):
        ok = True
        for a,b in zip(perm, perm[1:]):
            if frozenset((a,b)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def is_hamiltonian_cycle(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n < 3:
        return False
    if n == 3:
        # triangle required
        required = {frozenset((0,1)), frozenset((1,2)), frozenset((2,0))}
        return required.issubset(edges)
    # general case: check permutations with first vertex fixed to 0 to avoid rotations
    verts = list(range(n))
    for perm in itertools.permutations(verts[1:]):
        cycle = (0,)+perm
        ok = True
        for a,b in zip(cycle, cycle[1:]):
            if frozenset((a,b)) not in edges:
                ok = False
                break
        # edge from last back to first
        if ok and frozenset((cycle[-1], cycle[0])) not in edges:
            ok = False
        if ok:
            return True
    return False

def all_graphs(n):
    verts = list(range(n))
    possible_edges = [(i,j) for i in range(n) for j in range(i+1,n)]
    for mask in range(1<<len(possible_edges)):
        edges = []
        for idx,(u,v) in enumerate(possible_edges):
            if mask>>idx & 1:
                edges.append([u,v])
        yield {"n": n, "edges": edges}

tests_run = 0
tests_passed = 0
for n in range(0,6):
    for instance in all_graphs(n):
        # validate instances (should not raise)
        HamiltonianPath.validate(instance)
        path_ans = is_hamiltonian_path(instance)
        reduced = reduce(instance)
        HamiltonianCycle.validate(reduced)
        cycle_ans = is_hamiltonian_cycle(reduced)
        if path_ans == cycle_ans:
            tests_passed += 1
        else:
            print("Mismatch! n=",n,"instance",instance,"path",path_ans,"cycle",cycle_ans)
        tests_run += 1

verdict = {
    "verified": tests_run == tests_passed,
    "tests_run": tests_run,
    "tests_passed": tests_passed,
}
print(json.dumps(verdict))
with open('verdict.json','w') as f:
    json.dump(verdict, f)
