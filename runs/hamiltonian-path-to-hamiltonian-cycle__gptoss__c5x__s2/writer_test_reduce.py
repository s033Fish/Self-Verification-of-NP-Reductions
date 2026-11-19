import itertools
import random
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
        return [0,1] in [list(e) for e in edges] or [1,0] in [list(e) for e in edges]
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
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n <= 2:
        return False
    if n == 3:
        # triangle only
        required = {frozenset((0,1)), frozenset((1,2)), frozenset((2,0))}
        return required.issubset(edges)
    # brute force cycles (permutations fixing start at 0 to avoid rotations)
    verts = list(range(n))
    for perm in itertools.permutations(verts[1:]):
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

def random_graph(n, edge_prob=0.5):
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u,v])
    return {"n": n, "edges": edges}

def run_tests(num_trials=200):
    tests = 0
    passed = 0
    for n in range(0,6):
        # generate some random graphs for each n
        for _ in range(num_trials):
            inst = random_graph(n, edge_prob=0.5)
            # validate source
            HamiltonianPath.validate(inst)
            # compute answers
            ans_path = is_hamiltonian_path(inst)
            red = reduce(inst)
            # validate target
            HamiltonianCycle.validate(red)
            ans_cycle = is_hamiltonian_cycle(red)
            tests += 1
            if ans_path == ans_cycle:
                passed += 1
            else:
                print("Mismatch!", inst, red, ans_path, ans_cycle)
                return tests, passed, False
    return tests, passed, True

if __name__ == "__main__":
    total, good, ok = run_tests()
    verdict = {"verified": ok, "tests_run": total, "tests_passed": good}
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
