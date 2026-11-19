import itertools
import random
import sys
from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce

def is_hamiltonian_cycle(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n <= 2:
        return False
    if n == 3:
        # triangle required
        return all(frozenset({i, (i+1)%3}) in edges for i in range(3))
    # brute force permutations of vertices, fix start at 0 to avoid rotations
    verts = list(range(n))
    for perm in itertools.permutations(verts[1:]):
        path = (0,) + perm
        ok = True
        for i in range(n):
            u = path[i]
            v = path[(i+1)%n]
            if frozenset({u, v}) not in edges:
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
        return frozenset({0,1}) in edges
    verts = list(range(n))
    for perm in itertools.permutations(verts):
        ok = True
        for i in range(n-1):
            if frozenset({perm[i], perm[i+1]}) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def random_graph(n, p=0.5):
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}

def run_tests():
    total = 0
    passed = 0
    # exhaustive for n up to 4
    for n in range(0,5):
        vertices = list(range(n))
        all_possible_edges = [(u,v) for u in vertices for v in vertices if u<v]
        for mask in range(1<<len(all_possible_edges)):
            edges = []
            for i, (u,v) in enumerate(all_possible_edges):
                if mask & (1<<i):
                    edges.append([u,v])
            instance = {"n": n, "edges": edges}
            # validate
            try:
                HamiltonianCycle.validate(instance)
                HamiltonianPath.validate(instance)
            except Exception:
                continue
            total += 1
            ans_cycle = is_hamiltonian_cycle(instance)
            reduced = reduce(instance)
            ans_path = is_hamiltonian_path(reduced)
            if ans_cycle == ans_path:
                passed += 1
            else:
                print("FAIL", instance, "reduced", reduced, ans_cycle, ans_path)
                sys.exit(1)
    # random tests for n=5,6
    for n in [5,6]:
        for _ in range(200):
            instance = random_graph(n, 0.4)
            try:
                HamiltonianCycle.validate(instance)
            except Exception:
                continue
            total += 1
            ans_cycle = is_hamiltonian_cycle(instance)
            reduced = reduce(instance)
            ans_path = is_hamiltonian_path(reduced)
            if ans_cycle == ans_path:
                passed += 1
            else:
                print("FAIL random", instance, reduced)
                sys.exit(1)
    print(f"Tests run: {total}, passed: {passed}")
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    import json
    verdict = {"verified": passed==total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
