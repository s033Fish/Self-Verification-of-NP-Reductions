import itertools
import random
from problems import VertexCover, SetCover
from reduce import reduce

def vertex_cover_bruteforce(instance):
    VertexCover.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    # quick edge cases
    if not edges:
        return True
    if k >= n:
        return True
    vertices = list(range(n))
    for r in range(k+1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            s = set(subset)
            for u, v in edges:
                if u not in s and v not in s:
                    covered = False
                    break
            if covered:
                return True
    return False

def set_cover_bruteforce(instance):
    SetCover.validate(instance)
    u = instance["universe_size"]
    sets = instance["sets"]
    k = instance["k"]
    if k < 0:
        return False
    if u == 0:
        return True
    # check if any element missing entirely
    all_elements = set(range(u))
    covered_by_any = set()
    for s in sets:
        covered_by_any.update(s)
    if not all_elements.issubset(covered_by_any):
        return False
    if k >= len(sets):
        return True
    indices = list(range(len(sets)))
    for r in range(k+1):
        for combo in itertools.combinations(indices, r):
            covered = set()
            for i in combo:
                covered.update(sets[i])
            if covered == all_elements:
                return True
    return False

def random_instance(max_n=5, max_edges=8):
    n = random.randint(0, max_n)
    possible_edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    m = random.randint(0, min(len(possible_edges), max_edges))
    edges = random.sample(possible_edges, m)
    # convert to list of lists
    edges = [list(e) for e in edges]
    k = random.randint(-1, max(n, m)+2)
    return {"n": n, "edges": edges, "k": k}

def run_tests(num_trials=200):
    for _ in range(num_trials):
        vc = random_instance()
        sc = reduce(vc)
        vc_ans = vertex_cover_bruteforce(vc)
        sc_ans = set_cover_bruteforce(sc)
        if vc_ans != sc_ans:
            print("Mismatch!", vc, sc, vc_ans, sc_ans)
            return False
    return True

if __name__ == "__main__":
    ok = run_tests(500)
    print("All tests passed" if ok else "Some tests failed")
