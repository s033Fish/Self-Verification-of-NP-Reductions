import itertools
import random
import json
from problems import VertexCover, SetCover
from reduce import reduce

def vertex_cover_bruteforce(instance):
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    # trivial yes cases
    if not edges:
        return True
    if k >= n:
        return True
    for r in range(k+1):
        for subset in itertools.combinations(range(n), r):
            covered = True
            for u,v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False

def set_cover_bruteforce(instance):
    u = instance["universe_size"]
    sets = [set(s) for s in instance["sets"]]
    k = instance["k"]
    if k < 0:
        return False
    if u == 0:
        return True
    # check if any element uncovered by any set
    all_elements = set(range(u))
    if not any(all_elements.issubset(set().union(*sets)) for _ in [0]):
        # We'll handle later in search; but if some element never appears, return False
        for elem in all_elements:
            if not any(elem in s for s in sets):
                return False
    for r in range(k+1):
        for combo in itertools.combinations(range(len(sets)), r):
            covered = set()
            for idx in combo:
                covered |= sets[idx]
            if covered == all_elements:
                return True
    return False

def random_vertex_cover_instance(max_n=5, max_edges=6):
    n = random.randint(0, max_n)
    possible_edges = [(i,j) for i in range(n) for j in range(i+1,n)]
    m = random.randint(0, min(len(possible_edges), max_edges))
    edges = random.sample(possible_edges, m)
    # ensure format list of lists
    edges = [list(e) for e in edges]
    k = random.randint(-1, n+1)
    return {"n": n, "edges": edges, "k": k}

def run_tests(num=200):
    passed = 0
    for _ in range(num):
        src = random_vertex_cover_instance()
        # validate source
        VertexCover.validate(src)
        tgt = reduce(src)
        SetCover.validate(tgt)
        src_ans = vertex_cover_bruteforce(src)
        tgt_ans = set_cover_bruteforce(tgt)
        if src_ans != tgt_ans:
            print("Mismatch!", src, src_ans, tgt, tgt_ans)
            return False, passed
        passed += 1
    return True, passed

if __name__ == "__main__":
    ok, cnt = run_tests(500)
    result = {"verified": ok, "tests_run": cnt, "tests_passed": cnt if ok else cnt}
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
