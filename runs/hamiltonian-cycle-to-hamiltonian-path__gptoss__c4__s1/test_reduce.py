import itertools
import json
from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce

def is_hamiltonian_cycle(inst):
    n = inst["n"]
    edges = set(frozenset(e) for e in inst["edges"])
    if n <= 2:
        return False
    if n == 3:
        # triangle check
        needed = {frozenset((0,1)), frozenset((1,2)), frozenset((0,2))}
        return needed.issubset(edges)
    # brute force permutations of vertices, fix start at 0 to avoid rotations
    verts = list(range(n))
    for perm in itertools.permutations(verts[1:]):
        path = (0,)+perm
        ok = True
        for i in range(n):
            u = path[i]
            v = path[(i+1)%n]
            if frozenset((u,v)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def is_hamiltonian_path(inst):
    n = inst["n"]
    edges = set(frozenset(e) for e in inst["edges"])
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        return frozenset((0,1)) in edges
    verts = list(range(n))
    for perm in itertools.permutations(verts):
        ok = True
        for i in range(n-1):
            if frozenset((perm[i], perm[i+1])) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def generate_instances(max_n=5):
    for n in range(max_n+1):
        possible_edges = [(i,j) for i in range(n) for j in range(i+1,n)]
        for r in range(len(possible_edges)+1):
            for combo in itertools.combinations(possible_edges, r):
                inst = {"n": n, "edges": [list(e) for e in combo]}
                # validate both problems (should be same format)
                HamiltonianCycle.validate(inst)
                HamiltonianPath.validate(inst)
                yield inst


tests_run = 0
tests_passed = 0
for inst in generate_instances(5):
    tests_run += 1
    src_ans = is_hamiltonian_cycle(inst)
    red = reduce(inst)
    tgt_ans = is_hamiltonian_path(red)
    if src_ans == tgt_ans:
        tests_passed += 1
    else:
        print("Mismatch!", inst, src_ans, red, tgt_ans)
        break

verdict = {
    "verified": tests_run == tests_passed,
    "tests_run": tests_run,
    "tests_passed": tests_passed,
}
print(json.dumps(verdict))
with open('verdict.json','w') as f:
    json.dump(verdict, f)
