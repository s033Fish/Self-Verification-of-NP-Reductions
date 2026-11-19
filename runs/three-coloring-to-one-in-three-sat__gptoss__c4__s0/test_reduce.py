import random
import itertools
import json
from problems import ThreeColoring, OneInThreeSat
from reduce import reduce

def three_coloring_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    for assign in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if assign[u] == assign[v]:
                ok = False
                break
        if ok:
            return True
    return False

def one_in_three_sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in itertools.product([0, 1], repeat=m):
        ok = True
        for a, b, c in clauses:
            cnt = bits[a-1] + bits[b-1] + bits[c-1]
            if cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False

def random_graph(max_n=3, edge_prob=0.5):
    """Generate a random small graph for testing."""
    n = random.randint(0, max_n)
    edges: list[list[int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < edge_prob:
                edges.append([i, j])
    return {"n": n, "edges": edges}

def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        g = random_graph()
        ThreeColoring.validate(g)
        red = reduce(g)
        OneInThreeSat.validate(red)
        # limit size for brute‑force SAT
        if red['num_vars'] > 20:
            continue
        ans_src = three_coloring_bruteforce(g)
        ans_tgt = one_in_three_sat_bruteforce(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('FAIL')
            print('graph', g)
            print('reduction', red)
            print('src', ans_src, 'tgt', ans_tgt)
            break
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_tests(200)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict, indent=2))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
