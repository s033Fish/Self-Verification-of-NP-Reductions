import random
import itertools
import json
from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce

def solve_hamiltonian_cycle(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    # Edge cases
    if n <= 2:
        return False
    if n == 3:
        # triangle required
        return all(frozenset([i, (i+1)%3]) in edges for i in range(3))
    # brute force permutations of vertices
    verts = list(range(n))
    for perm in itertools.permutations(verts):
        ok = True
        for i in range(n):
            u = perm[i]
            v = perm[(i+1)%n]
            if frozenset([u, v]) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def solve_hamiltonian_path(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        return frozenset([0,1]) in edges
    verts = list(range(n))
    for perm in itertools.permutations(verts):
        ok = True
        for i in range(n-1):
            if frozenset([perm[i], perm[i+1]]) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def random_graph(max_n=6):
    n = random.randint(0, max_n)
    possible = [(i,j) for i in range(n) for j in range(i+1,n)]
    edges = []
    for (i,j) in possible:
        if random.choice([True, False]):
            edges.append([i,j])
    return {"n": n, "edges": edges}

tests = 200
passed = 0
for _ in range(tests):
    inst = random_graph()
    # Validate instance (will raise if invalid)
    HamiltonianCycle.validate(inst)
    reduced = reduce(inst)
    # Ensure reduced instance valid for path
    HamiltonianPath.validate(reduced)
    ans_cycle = solve_hamiltonian_cycle(inst)
    ans_path = solve_hamiltonian_path(reduced)
    if ans_cycle == ans_path:
        passed += 1
    else:
        print("Mismatch!", inst, reduced, ans_cycle, ans_path)
        break

# Write verdict
verdict = {
    "verified": passed == tests,
    "tests_run": tests,
    "tests_passed": passed,
}
with open('verdict.json', 'w') as f:
    json.dump(verdict, f, indent=2)
print(json.dumps(verdict))
