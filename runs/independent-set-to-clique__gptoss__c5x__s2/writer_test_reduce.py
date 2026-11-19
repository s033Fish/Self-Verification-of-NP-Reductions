import itertools
import json
from problems import IndependentSet, Clique
from reduce import reduce


def brute_independent_set(instance):
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    # check all subsets of size >= k
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def brute_clique(instance):
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def generate_all_graphs(n):
    # generate all possible undirected edges without self-loops
    vertices = list(range(n))
    possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
    for mask in range(1 << len(possible_edges)):
        edges = []
        for i, (u, v) in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append([u, v])
        yield edges


def run_tests():
    total = 0
    passed = 0
    for n in range(1, 6):  # up to 5 vertices for exhaustive testing
        for edges in generate_all_graphs(n):
            for k in range(-1, n + 2):  # include some out‑of‑range ks
                instance = {"n": n, "edges": edges, "k": k}
                # validate source
                IndependentSet.validate(instance)
                # compute answers
                src_ans = brute_independent_set(instance)
                tgt_instance = reduce(instance)
                Clique.validate(tgt_instance)
                tgt_ans = brute_clique(tgt_instance)
                total += 1
                if src_ans == tgt_ans:
                    passed += 1
                else:
                    print("Mismatch!", instance, src_ans, tgt_ans)
                    return total, passed, False
    return total, passed, True

if __name__ == "__main__":
    total, passed, ok = run_tests()
    verdict = {"verified": ok, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
