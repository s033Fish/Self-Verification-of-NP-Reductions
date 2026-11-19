import itertools
import json
import sys
from problems import HamiltonianCycle, HamiltonianPath, InvalidInstance
from reduce import reduce

def hamiltonian_cycle_bruteforce(instance):
    n = instance["n"]
    edges_set = {frozenset(e) for e in instance["edges"]}
    if n <= 2:
        return False
    if n == 3:
        # triangle check
        return all(frozenset([i, (i+1)%3]) in edges_set for i in range(3))
    # try all permutations starting at 0 to avoid cycles rotation symmetry
    verts = list(range(n))
    for perm in itertools.permutations(verts[1:]):
        path = (0,) + perm
        # check edges between consecutive and last to first
        ok = True
        for i in range(n):
            u = path[i]
            v = path[(i+1)%n]
            if frozenset([u, v]) not in edges_set:
                ok = False
                break
        if ok:
            return True
    return False

def hamiltonian_path_bruteforce(instance):
    n = instance["n"]
    edges_set = {frozenset(e) for e in instance["edges"]}
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        return frozenset([0,1]) in edges_set
    verts = list(range(n))
    for perm in itertools.permutations(verts):
        ok = True
        for i in range(n-1):
            if frozenset([perm[i], perm[i+1]]) not in edges_set:
                ok = False
                break
        if ok:
            return True
    return False

def generate_all_graphs(n):
    verts = list(range(n))
    possible_edges = []
    for i in range(n):
        for j in range(i+1, n):
            possible_edges.append([i,j])
    m = len(possible_edges)
    for mask in range(1<<m):
        edges = []
        for idx in range(m):
            if mask & (1<<idx):
                edges.append(possible_edges[idx][:])
        yield {"n": n, "edges": edges}

def main():
    total = 0
    passed = 0
    for n in range(0,6):  # up to 5 vertices
        for instance in generate_all_graphs(n):
            # validate instance
            try:
                HamiltonianCycle.validate(instance)
            except InvalidInstance:
                continue  # should not happen
            src_ans = hamiltonian_cycle_bruteforce(instance)
            reduced = reduce(instance)
            tgt_ans = hamiltonian_path_bruteforce(reduced)
            total += 1
            if src_ans == tgt_ans:
                passed += 1
            else:
                print("Mismatch! n=", n, "instance=", instance, "src=", src_ans, "tgt=", tgt_ans, file=sys.stderr)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result))
    # write verdict.json
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
    sys.exit(0 if result["verified"] else 1)

if __name__ == "__main__":
    main()
