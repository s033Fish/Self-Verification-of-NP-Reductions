import random
import itertools
import json
from problems import IndependentSet, VertexCover, InvalidInstance
from reduce import reduce

def independent_set_bruteforce(instance):
    n = instance['n']
    edges = [(u, v) for u, v in instance['edges']]
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # generate subsets of vertices
    verts = list(range(n))
    for r in range(k, n+1):
        for subset in itertools.combinations(verts, r):
            # check independence
            ok = True
            s = set(subset)
            for u, v in edges:
                if u in s and v in s:
                    ok = False
                    break
            if ok:
                return True
    return False

def vertex_cover_bruteforce(instance):
    n = instance['n']
    edges = [(u, v) for u, v in instance['edges']]
    k = instance['k']
    if k < 0:
        return False
    if k >= n:
        return True
    verts = list(range(n))
    for r in range(0, k+1):
        for subset in itertools.combinations(verts, r):
            s = set(subset)
            ok = True
            for u, v in edges:
                if u not in s and v not in s:
                    ok = False
                    break
            if ok:
                return True
    return False

def random_graph(max_n=6, edge_prob=0.3):
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return n, edges

def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        n, edges = random_graph()
        # choose k in a range that includes negatives and >n
        k = random.randint(-2, n+2)
        indep_instance = {'n': n, 'edges': edges, 'k': k}
        # validate
        try:
            IndependentSet.validate(indep_instance)
        except InvalidInstance:
            continue  # shouldn't happen
        # compute answers
        ans_indep = independent_set_bruteforce(indep_instance)
        # reduce
        vc_instance = reduce(indep_instance)
        # validate target
        VertexCover.validate(vc_instance)
        ans_vc = vertex_cover_bruteforce(vc_instance)
        # The answers should be equal (yes iff yes)
        if ans_indep == ans_vc:
            passed += 1
        else:
            print('Mismatch!')
            print('Indep:', indep_instance, ans_indep)
            print('VC:', vc_instance, ans_vc)
            break
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_tests()
    result = {
        'verified': passed == total,
        'tests_run': total,
        'tests_passed': passed,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
