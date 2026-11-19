import random
import itertools
import json
from problems import VertexCover, SetCover
from reduce import reduce


def solve_vertex_cover(inst):
    n = inst["n"]
    edges = inst["edges"]
    k = inst["k"]
    if k < 0:
        return False
    # trivial yes cases handled by brute force as well
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


def solve_set_cover(inst):
    u = inst["universe_size"]
    sets = inst["sets"]
    k = inst["k"]
    if k < 0:
        return False
    # universe elements are 0..u-1
    universe = set(range(u))
    m = len(sets)
    for r in range(0, min(k, m) + 1):
        for combo in itertools.combinations(range(m), r):
            covered = set()
            for idx in combo:
                covered.update(sets[idx])
            if covered == universe:
                return True
    return False


def random_instance(max_n=5, max_edges=10):
    n = random.randint(0, max_n)
    # generate possible edges without duplicates
    possible = [(i, j) for i in range(n) for j in range(i+1, n)]
    random.shuffle(possible)
    m = random.randint(0, min(len(possible), max_edges))
    edges = [list(e) for e in possible[:m]]
    k = random.randint(-1, max(n, 3))
    return {"n": n, "edges": edges, "k": k}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        vc_inst = random_instance()
        # validate
        VertexCover.validate(vc_inst)
        sc_inst = reduce(vc_inst)
        SetCover.validate(sc_inst)
        ans_vc = solve_vertex_cover(vc_inst)
        ans_sc = solve_set_cover(sc_inst)
        if ans_vc == ans_sc:
            passed += 1
        else:
            print("Mismatch!", vc_inst, sc_inst, ans_vc, ans_sc)
            break
    return passed, num

if __name__ == "__main__":
    passed, total = run_tests(500)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
