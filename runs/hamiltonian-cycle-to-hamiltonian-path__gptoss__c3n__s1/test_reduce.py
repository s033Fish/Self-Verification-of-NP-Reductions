import itertools
import random
import json
from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce

def is_hamiltonian_cycle(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n <= 2:
        return False
    if n == 3:
        # triangle needed
        return all(frozenset([i, (i+1)%3]) in edges for i in range(3))
    vertices = list(range(n))
    for perm in itertools.permutations(vertices):
        # fix start to reduce symmetry
        if perm[0] != 0:
            continue
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

def is_hamiltonian_path(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        return frozenset([0,1]) in edges
    vertices = list(range(n))
    for perm in itertools.permutations(vertices):
        ok = True
        for i in range(n-1):
            if frozenset([perm[i], perm[i+1]]) not in edges:
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
                edges.append([i,j])
    return {"n": n, "edges": edges}


def run_tests(num_trials=200):
    passed = 0
    total = 0
    for n in range(0,7):
        for _ in range(num_trials):
            inst = random_graph(n, p=0.5)
            # validate both instances
            HamiltonianCycle.validate(inst)
            # reduce
            red = reduce(inst)
            HamiltonianPath.validate(red)
            ans_cycle = is_hamiltonian_cycle(inst)
            ans_path = is_hamiltonian_path(red)
            if ans_cycle == ans_path:
                passed += 1
            else:
                print("Mismatch!", inst, red, ans_cycle, ans_path)
            total += 1
    # also test edge cases explicitly
    edge_cases = [
        {"n":0,"edges":[]},
        {"n":1,"edges":[]},
        {"n":2,"edges":[]},
        {"n":2,"edges":[[0,1]]},
        {"n":3,"edges":[[0,1],[1,2],[2,0]]},
        {"n":3,"edges":[[0,1],[1,2]]},
    ]
    for inst in edge_cases:
        HamiltonianCycle.validate(inst)
        red = reduce(inst)
        HamiltonianPath.validate(red)
        if is_hamiltonian_cycle(inst) == is_hamiltonian_path(red):
            passed += 1
        else:
            print("Mismatch edge case", inst, red)
        total += 1
    return passed, total

if __name__ == "__main__":
    passed, total = run_tests()
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(result, f)
    print(result)
