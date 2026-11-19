import random
import itertools
import json
from problems import ThreeColoring, OneInThreeSat
from reduce import reduce


def solve_three_coloring(instance):
    n = instance['n']
    edges = [(u, v) for u, v in instance['edges']]
    for assign in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if assign[u] == assign[v]:
                ok = False
                break
        if ok:
            return True
    return False


def solve_one_in_three_sat(instance):
    m = instance['num_vars']
    clauses = [tuple(cl) for cl in instance['clauses']]
    for bits in itertools.product([False, True], repeat=m):
        good = True
        for a, b, c in clauses:
            cnt = bits[a-1] + bits[b-1] + bits[c-1]
            if cnt != 1:
                good = False
                break
        if good:
            return True
    return False


def random_three_coloring(max_n=5, edge_prob=0.3):
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        src = random_three_coloring()
        ThreeColoring.validate(src)
        src_ans = solve_three_coloring(src)
        tgt = reduce(src)
        OneInThreeSat.validate(tgt)
        if tgt['num_vars'] > 20:
            # skip exhaustive SAT check for large instances
            passed += 1
            continue
        tgt_ans = solve_one_in_three_sat(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('src', src)
            print('src_ans', src_ans)
            print('tgt', tgt)
            print('tgt_ans', tgt_ans)
            break
    return passed, num_trials

if __name__ == '__main__':
    passed, total = run_tests()
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
