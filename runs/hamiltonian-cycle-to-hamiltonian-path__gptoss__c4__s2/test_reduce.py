import itertools
import json
import os
import sys

# Import the problems and reduction
from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce as reduce_instance

def is_hamiltonian_cycle(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n <= 2:
        return False
    if n == 3:
        # triangle required
        required = {frozenset([0,1]), frozenset([1,2]), frozenset([0,2])}
        return required.issubset(edges)
    # brute force permutations of vertices starting at 0 to avoid cycles rotations
    verts = list(range(n))
    for perm in itertools.permutations(verts[1:]):
        cycle = (0,)+perm
        ok = True
        for i in range(n):
            u = cycle[i]
            v = cycle[(i+1)%n]
            if frozenset([u,v]) not in edges:
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
    # brute force permutations of all vertices
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

def generate_all_graphs(n):
    vertices = list(range(n))
    possible_edges = list(itertools.combinations(vertices, 2))
    for mask in range(1 << len(possible_edges)):
        edges = []
        for i, e in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append([e[0], e[1]])
        yield {"n": n, "edges": edges}

def run_tests(max_n=5):
    total = 0
    passed = 0
    for n in range(max_n+1):
        for instance in generate_all_graphs(n):
            # validate source instance
            try:
                HamiltonianCycle.validate(instance)
            except Exception:
                continue  # skip invalid (shouldn't happen)
            src_ans = is_hamiltonian_cycle(instance)
            reduced = reduce_instance(instance)
            # validate target instance
            HamiltonianPath.validate(reduced)
            tgt_ans = is_hamiltonian_path(reduced)
            if src_ans == tgt_ans:
                passed += 1
            else:
                print("Counterexample:")
                print(json.dumps(instance))
                print("src_ans", src_ans, "tgt_ans", tgt_ans)
                print("reduced", json.dumps(reduced))
                sys.exit(1)
            total += 1
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests(5)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))
