import random
import itertools
import sys
from problems import IndependentSet, VertexCover
from reduce import reduce as reduction


def independent_set_bruteforce(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # enumerate subsets
    for r in range(k, n+1):
        for subset in itertools.combinations(range(n), r):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def vertex_cover_bruteforce(instance):
    n = instance['n']
    edges = [tuple(e) for e in instance['edges']]
    k = instance['k']
    if k < 0:
        return False
    if k >= n:
        return True
    # need subset size <= k covering all edges
    for r in range(0, k+1):
        for subset in itertools.combinations(range(n), r):
            covered = True
            subset_set = set(subset)
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False


def random_instance(max_n=7):
    n = random.randint(0, max_n)
    # generate each possible edge with 50% probability
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.choice([True, False]):
                edges.append([u, v])
    k = random.randint(-2, n+2)  # allow out-of-range k to test edge cases
    return {'n': n, 'edges': edges, 'k': k}


def run_tests(num_trials=200):
    for i in range(num_trials):
        src = random_instance()
        # validate source
        try:
            IndependentSet.validate(src)
        except Exception as e:
            print('Invalid source instance generated', src, e)
            sys.exit(1)
        src_ans = independent_set_bruteforce(src)
        tgt = reduction(src)
        # validate target
        try:
            VertexCover.validate(tgt)
        except Exception as e:
            print('Invalid target instance', tgt, e)
            sys.exit(1)
        tgt_ans = vertex_cover_bruteforce(tgt)
        if src_ans != tgt_ans:
            print('Mismatch on trial', i)
            print('Source:', src, 'src_ans', src_ans)
            print('Target:', tgt, 'tgt_ans', tgt_ans)
            sys.exit(1)
    print('All tests passed', num_trials)

if __name__ == '__main__':
    run_tests()
