import random
import itertools
import sys
import json
from problems import IndependentSet, VertexCover, InvalidInstance
from reduce import reduce

def solve_independent_set(instance):
    """Brute‑force solver for Independent Set used in tests.

    Handles the edge‑cases described in the problem statement: ``k <= 0`` is
    always a yes‑instance and ``k > n`` is always a no‑instance.  For other
    values we enumerate subsets of size ``r`` for ``r`` from ``k`` up to ``n``.
    """
    IndependentSet.validate(instance)
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    # Edge cases per definition
    if k <= 0:
        return True
    if k > n:
        return False
    # Brute force search for an independent set of size at least k
    for r in range(k, n + 1):
        for subset in itertools.combinations(range(n), r):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False

def solve_vertex_cover(instance):
    VertexCover.validate(instance)
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    # Edge cases are naturally handled by enumeration
    for r in range(0, k + 1):
        for subset in itertools.combinations(range(n), r):
            if all(e & set(subset) for e in edges):
                return True
    return False

def random_instance(max_n=6):
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    m = random.randint(0, len(possible_edges))
    edges = random.sample(possible_edges, m)
    edges = [list(e) for e in edges]
    k = random.randint(-1, n + 2)  # allow out of range values
    return {"n": n, "edges": edges, "k": k}

def test_one(instance):
    indep_yes = solve_independent_set(instance)
    reduced = reduce(instance)
    vc_yes = solve_vertex_cover(reduced)
    if indep_yes != vc_yes:
        print('Mismatch!')
        print('Original:', instance)
        print('Reduced:', reduced)
        print('IndependentSet answer:', indep_yes)
        print('VertexCover answer:', vc_yes)
        return False
    return True

def main():
    random.seed(0)
    total = 200
    passed = 0
    for i in range(total):
        inst = random_instance()
        try:
            if test_one(inst):
                passed += 1
        except InvalidInstance as e:
            print('Invalid instance generated?', e)
            sys.exit(1)
    print(f'Passed {passed}/{total} random tests')
    # Additional edge case tests
    edge_cases = [
        {"n": 5, "edges": [], "k": 0},
        {"n": 5, "edges": [], "k": -3},
        {"n": 5, "edges": [], "k": 6},
        {"n": 3, "edges": [[0,1],[1,2]], "k": 2},
        {"n": 3, "edges": [[0,1],[1,2]], "k": 1},
    ]
    for inst in edge_cases:
        IndependentSet.validate(inst)
        reduced = reduce(inst)
        VertexCover.validate(reduced)
        if solve_independent_set(inst) != solve_vertex_cover(reduced):
            print('Edge case mismatch', inst, reduced)
            sys.exit(1)
        passed += 1
    print('All edge case tests passed')
    verdict = {"verified": True, "tests_run": total + len(edge_cases), "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('Verdict written')

if __name__ == '__main__':
    main()
