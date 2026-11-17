import itertools
import json
from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce

def solve_path(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        return frozenset([0,1]) in edges
    # try all permutations
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n-1):
            if frozenset([perm[i], perm[i+1]]) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def solve_cycle(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n < 3:
        return False
    # we can fix start at 0 to reduce symmetry
    vertices = list(range(n))
    for perm in itertools.permutations(vertices[1:]):
        cycle = (0,) + perm
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


def all_graphs(n):
    # generate all undirected simple graphs on n vertices
    verts = list(range(n))
    possible_edges = [(i,j) for i in range(n) for j in range(i+1,n)]
    for mask in range(1<<len(possible_edges)):
        edges = []
        for idx, (u,v) in enumerate(possible_edges):
            if mask & (1<<idx):
                edges.append([u,v])
        yield {"n": n, "edges": edges}


def run_tests():
    total = 0
    passed = 0
    for n in range(0,6):
        for instance in all_graphs(n):
            total += 1
            # validate instance
            HamiltonianPath.validate(instance)
            src_ans = solve_path(instance)
            red = reduce(instance)
            # validate reduced instance
            HamiltonianCycle.validate(red)
            tgt_ans = solve_cycle(red)
            if src_ans == tgt_ans:
                passed += 1
            else:
                print("Mismatch! n", n, "instance", instance, "src", src_ans, "tgt", tgt_ans)
                return total, passed, False
    return total, passed, True

if __name__ == "__main__":
    total, passed, ok = run_tests()
    verdict = {"verified": ok, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
