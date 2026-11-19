import random
import itertools
import sys
from problems import VertexCover, IndependentSet, InvalidInstance
from reduce import reduce

def brute_vertex_cover(instance):
    n = instance['n']
    edges = [(u, v) for u, v in instance['edges']]
    k = instance['k']
    if k < 0:
        return False
    if not edges:
        return True  # empty set covers
    if k >= n:
        return True
    # check all subsets of size up to k
    vertices = list(range(n))
    for r in range(k+1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            for u, v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False

def brute_independent_set(instance):
    n = instance['n']
    edges = set(frozenset((u, v)) for u, v in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    if not edges:
        return True
    vertices = list(range(n))
    # need at least k, so enumerate subsets of size >=k
    for r in range(k, n+1):
        for subset in itertools.combinations(vertices, r):
            ok = True
            for i in range(len(subset)):
                for j in range(i+1, len(subset)):
                    if frozenset((subset[i], subset[j])) in edges:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                return True
    return False

def random_instance(max_n=6):
    n = random.randint(0, max_n)
    # generate possible edges
    possible = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = []
    for (u, v) in possible:
        if random.random() < 0.3:
            edges.append([u, v])
    # choose k in range -1..n+1
    k = random.randint(-1, n+1)
    return {"n": n, "edges": edges, "k": k}

def test_one(instance):
    # validate source
    VertexCover.validate(instance)
    reduced = reduce(instance)
    IndependentSet.validate(reduced)
    vc = brute_vertex_cover(instance)
    iset = brute_independent_set(reduced)
    if vc != iset:
        print("Mismatch!", instance, reduced, vc, iset)
        return False
    return True

def main():
    random.seed(0)
    total = 200
    passed = 0
    for _ in range(total):
        inst = random_instance()
        try:
            if test_one(inst):
                passed += 1
        except InvalidInstance as e:
            print("Invalid instance generated", e)
            sys.exit(1)
    print(f"Passed {passed}/{total} tests")
    sys.exit(0 if passed == total else 1)

if __name__ == '__main__':
    main()
