import itertools
import random
import json
from problems import IndependentSet, Clique
from reduce import reduce


def solve_independent_set(inst):
    n = inst["n"]
    edges = set(frozenset(e) for e in inst["edges"])
    k = inst["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    # brute force subsets of size >= k
    vertices = list(range(n))
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def solve_clique(inst):
    n = inst["n"]
    edges = set(frozenset(e) for e in inst["edges"])
    k = inst["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    vertices = list(range(n))
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
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
                edges.append([u, v])
    return edges


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        n = random.randint(0, 6)
        edges = random_graph(n, edge_prob=0.5)
        k = random.randint(-1, n+2)  # include edge cases
        indep_inst = {"n": n, "edges": edges, "k": k}
        # validate
        IndependentSet.validate(indep_inst)
        # reduce
        clique_inst = reduce(indep_inst)
        Clique.validate(clique_inst)
        # compare answers
        ans_indep = solve_independent_set(indep_inst)
        ans_clique = solve_clique(clique_inst)
        if ans_indep == ans_clique:
            passed += 1
        else:
            print("FAIL", indep_inst, clique_inst, ans_indep, ans_clique)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests(500)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
