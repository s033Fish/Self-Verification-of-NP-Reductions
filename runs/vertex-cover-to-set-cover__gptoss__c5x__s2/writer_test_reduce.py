import itertools
import random
import json
from problems import VertexCover, SetCover, InvalidInstance
from reduce import reduce


def vertex_cover_bruteforce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    # trivial yes cases
    if k >= n:
        return True
    if not edges:
        return True
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            for u, v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False


def set_cover_bruteforce(instance):
    u = instance["universe_size"]
    sets = instance["sets"]
    k = instance["k"]
    if k < 0:
        return False
    if u == 0:
        return True
    # check that every element appears in at least one set
    all_elements = set(range(u))
    present = set()
    for s in sets:
        present.update(s)
    if not all_elements.issubset(present):
        return False
    m = len(sets)
    for r in range(k + 1):
        for combo in itertools.combinations(range(m), r):
            covered = set()
            for idx in combo:
                covered.update(sets[idx])
            if covered >= all_elements:
                return True
    return False


def random_vertex_cover_instance(max_n=5, max_edges=10):
    n = random.randint(0, max_n)
    possible_edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    m = random.randint(0, min(len(possible_edges), max_edges))
    edges = random.sample(possible_edges, m)
    # convert to list of lists
    edges = [list(e) for e in edges]
    k = random.randint(-1, n+2)  # allow out of range
    return {"n": n, "edges": edges, "k": k}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        src = random_vertex_cover_instance()
        # validate source
        try:
            VertexCover.validate(src)
        except InvalidInstance:
            continue  # shouldn't happen
        tgt = reduce(src)
        # validate target
        SetCover.validate(tgt)
        ans_src = vertex_cover_bruteforce(src)
        ans_tgt = set_cover_bruteforce(tgt)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", src, tgt, ans_src, ans_tgt)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests()
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
