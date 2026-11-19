import random
import itertools
import json
from problems import IndependentSet, VertexCover, InvalidInstance
from reduce import reduce

def brute_independent_set(inst):
    n = inst["n"]
    edges = set(frozenset(e) for e in inst["edges"])
    k = inst["k"]
    # Edge cases
    if k <= 0:
        return True
    if k > n:
        return False
    # brute force subsets
    for subset in itertools.combinations(range(n), k):
        ok = True
        for u, v in itertools.combinations(subset, 2):
            if frozenset((u, v)) in edges:
                ok = False
                break
        if ok:
            return True
    return False

def brute_vertex_cover(inst):
    n = inst["n"]
    edges = [tuple(e) for e in inst["edges"]]
    k = inst["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        return True
    for size in range(k + 1):
        for subset in itertools.combinations(range(n), size):
            covered = True
            for u, v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False

def random_instance(max_n=6):
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u+1, n)]
    edges = []
    for (u, v) in possible_edges:
        if random.random() < 0.3:
            edges.append([u, v])
    k = random.randint(-2, n+2)
    return {"n": n, "edges": edges, "k": k}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        src = random_instance()
        # validate source
        try:
            IndependentSet.validate(src)
        except InvalidInstance:
            continue  # skip malformed (shouldn't happen)
        tgt = reduce(src)
        try:
            VertexCover.validate(tgt)
        except InvalidInstance as e:
            print("Target validation failed", e, src, tgt)
            return False, passed
        src_ans = brute_independent_set(src)
        tgt_ans = brute_vertex_cover(tgt)
        if src_ans != tgt_ans:
            print("Mismatch!", src, tgt, src_ans, tgt_ans)
            return False, passed
        passed += 1
    return True, passed

if __name__ == "__main__":
    ok, count = run_tests(500)
    result = {"verified": ok, "tests_run": 500, "tests_passed": count}
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
