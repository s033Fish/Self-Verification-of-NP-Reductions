import itertools
import random
import sys
from typing import List, Dict

import problems
from reduce import reduce


def vertex_cover_bruteforce(instance: Dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    # any subset up to k
    for r in range(k + 1):
        for subset in itertools.combinations(range(n), r):
            cover_set = set(subset)
            ok = True
            for u, v in edges:
                if u not in cover_set and v not in cover_set:
                    ok = False
                    break
            if ok:
                return True
    return False


def set_cover_bruteforce(instance: Dict) -> bool:
    u = instance["universe_size"]
    sets = instance["sets"]
    k = instance["k"]
    if k < 0:
        return False
    if u == 0:
        return True
    # Precompute coverage of each set as a set of elements
    set_elems = [set(s) for s in sets]
    # check if any element uncovered by any set
    all_elements = set(range(u))
    if not any(all_elements <= set().union(*set_elems)):
        # Actually we need to check if each element appears in at least one set
        for elem in all_elements:
            if not any(elem in s for s in set_elems):
                return False
    for r in range(k + 1):
        for combo in itertools.combinations(range(len(sets)), r):
            covered = set()
            for idx in combo:
                covered.update(set_elems[idx])
            if covered == all_elements:
                return True
    return False


def random_vertex_cover_instance(max_n=5, max_edges=10):
    n = random.randint(0, max_n)
    possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    m = random.randint(0, min(len(possible_edges), max_edges))
    edges = random.sample(possible_edges, m)
    k = random.randint(-1, n + 2)  # allow out of range
    return {"n": n, "edges": [list(e) for e in edges], "k": k}


def test_random_cases(num_cases=200):
    for _ in range(num_cases):
        inst = random_vertex_cover_instance()
        # validate source
        problems.VertexCover.validate(inst)
        vc_ans = vertex_cover_bruteforce(inst)
        reduced = reduce(inst)
        # validate target
        problems.SetCover.validate(reduced)
        sc_ans = set_cover_bruteforce(reduced)
        if vc_ans != sc_ans:
            print("Mismatch!", inst, reduced, vc_ans, sc_ans)
            return False
    return True

if __name__ == "__main__":
    ok = test_random_cases(500)
    sys.exit(0 if ok else 1)
