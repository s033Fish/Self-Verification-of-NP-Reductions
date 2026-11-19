import itertools
import random
import json
from problems import ThreeColoring, IndependentSet
from reduce import reduce

def solve_three_coloring(instance):
    n = instance["n"]
    edges = instance["edges"]
    # Edge cases from docstring can be handled implicitly
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False

def solve_independent_set(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    k = instance["k"]
    # trivial cases
    if k <= 0:
        return True
    if k > n:
        return False
    for size in range(k, n+1):
        for subset in itertools.combinations(range(n), size):
            good = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    good = False
                    break
            if good:
                return True
    return False


def generate_random_instance(max_n=5, edge_prob=0.3):
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def test_one(instance):
    ThreeColoring.validate(instance)
    reduced = reduce(instance)
    IndependentSet.validate(reduced)
    ans_src = solve_three_coloring(instance)
    ans_tgt = solve_independent_set(reduced)
    return ans_src == ans_tgt


def main():
    random.seed(0)
    total = 0
    passed = 0
    # exhaustive for n up to 4
    for n in range(0, 5):
        vertices = list(range(n))
        possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
        for mask in range(1 << len(possible_edges)):
            edges = []
            for i, (u, v) in enumerate(possible_edges):
                if mask & (1 << i):
                    edges.append([u, v])
            inst = {"n": n, "edges": edges}
            total += 1
            if test_one(inst):
                passed += 1
    # additional random tests
    for _ in range(200):
        inst = generate_random_instance()
        total += 1
        if test_one(inst):
            passed += 1
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict, indent=2))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == "__main__":
    main()
