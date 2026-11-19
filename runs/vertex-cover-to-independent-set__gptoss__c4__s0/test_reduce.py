import random
import itertools
import json
import sys
from problems import VertexCover, IndependentSet
from reduce import reduce

def vertex_cover_bruteforce(instance):
    n = instance['n']
    edges = [tuple(e) for e in instance['edges']]
    k = instance['k']
    if k < 0:
        return False
    # any subset of vertices of size <= k that covers all edges
    for r in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), r):
            covered = True
            s = set(subset)
            for u, v in edges:
                if u not in s and v not in s:
                    covered = False
                    break
            if covered:
                return True
    return False

def independent_set_bruteforce(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # any subset of size >= k that is independent
    for r in range(k, n+1):
        for subset in itertools.combinations(range(n), r):
            ok = True
            s = set(subset)
            for u, v in itertools.combinations(s, 2):
                if frozenset((u, v)) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False

def random_instance(max_n=6, edge_prob=0.3, k_range=(-2, 8)):
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    k = random.randint(k_range[0], k_range[1])
    return {"n": n, "edges": edges, "k": k}


def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        inst = random_instance()
        # Validate instances
        try:
            VertexCover.validate(inst)
            IndependentSet.validate(inst)  # same format
        except Exception as e:
            # Invalid instance, skip
            continue
        vc_ans = vertex_cover_bruteforce(inst)
        red = reduce(inst)
        # validate reduced instance for IndependentSet
        try:
            IndependentSet.validate(red)
        except Exception as e:
            print("Reduced instance invalid", red, e)
            sys.exit(1)
        is_ans = independent_set_bruteforce(red)
        if vc_ans == is_ans:
            passed += 1
        else:
            print("Mismatch on test", i)
            print("Original", inst, "vc_ans", vc_ans)
            print("Reduced", red, "is_ans", is_ans)
            sys.exit(1)
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_tests()
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
