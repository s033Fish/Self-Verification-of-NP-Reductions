import itertools
import random
import json
from problems import IndependentSet, Clique
from reduce import reduce


def is_independent_set(instance, subset):
    # subset is set of vertices
    edges = {frozenset(e) for e in instance['edges']}
    for u, v in itertools.combinations(subset, 2):
        if frozenset((u, v)) in edges:
            return False
    return True

def independent_set_bruteforce(instance):
    n = instance['n']
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    vertices = range(n)
    # check all subsets of size >= k
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            if is_independent_set(instance, set(subset)):
                return True
    return False

def is_clique(instance, subset):
    edges = {frozenset(e) for e in instance['edges']}
    for u, v in itertools.combinations(subset, 2):
        if frozenset((u, v)) not in edges:
            return False
    return True

def clique_bruteforce(instance):
    n = instance['n']
    k = instance['k']
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    vertices = range(n)
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            if is_clique(instance, set(subset)):
                return True
    return False

def generate_random_instance(n_max=5, trials=1000):
    instances = []
    for _ in range(trials):
        n = random.randint(0, n_max)
        possible_edges = [(u, v) for u in range(n) for v in range(u+1, n)]
        edges = []
        for u, v in possible_edges:
            if random.choice([True, False]):
                edges.append([u, v])
        k = random.randint(-1, n+2)  # include edge cases
        inst = {"n": n, "edges": edges, "k": k}
        # validate using problem classes
        IndependentSet.validate(inst)
        instances.append(inst)
    return instances


def run_tests():
    total = 0
    passed = 0
    # deterministic small graphs enumeration for n up to 4
    for n in range(0, 5):
        vertices = list(range(n))
        possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
        # iterate over all subsets of edges
        for edge_mask in range(1 << len(possible_edges)):
            edges = []
            for idx, (u, v) in enumerate(possible_edges):
                if (edge_mask >> idx) & 1:
                    edges.append([u, v])
            for k in range(-1, n+3):
                inst = {"n": n, "edges": edges, "k": k}
                IndependentSet.validate(inst)
                total += 1
                # compute answers
                ans_source = independent_set_bruteforce(inst)
                reduced = reduce(inst)
                Clique.validate(reduced)
                ans_target = clique_bruteforce(reduced)
                if ans_source == ans_target:
                    passed += 1
                else:
                    print("Mismatch!", inst, reduced, ans_source, ans_target)
                    return total, passed
    # also random tests
    for inst in generate_random_instance():
        total += 1
        ans_source = independent_set_bruteforce(inst)
        reduced = reduce(inst)
        Clique.validate(reduced)
        ans_target = clique_bruteforce(reduced)
        if ans_source == ans_target:
            passed += 1
        else:
            print("Random mismatch!", inst, reduced, ans_source, ans_target)
            break
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    result = {"verified": total == passed, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
