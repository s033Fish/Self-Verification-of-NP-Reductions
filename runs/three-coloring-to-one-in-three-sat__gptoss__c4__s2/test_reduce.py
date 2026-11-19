import itertools
from problems import ThreeColoring, OneInThreeSat
from reduce import reduce


def three_coloring_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def one_in_three_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for assignment in itertools.product([False, True], repeat=m):
        good = True
        for clause in clauses:
            true_count = sum(assignment[abs(lit)-1] for lit in clause)
            if true_count != 1:
                good = False
                break
        if good:
            return True
    return False


def generate_graphs(max_n=4, max_vars=15):
    """Generate all graphs up to max_n vertices but only keep those whose
    reduction yields at most max_vars SAT variables, to keep brute‑force feasible."""
    graphs = []
    for n in range(max_n + 1):
        possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
        for r in range(len(possible_edges) + 1):
            for edges in itertools.combinations(possible_edges, r):
                if 3 * n + 3 * len(edges) <= max_vars:
                    graphs.append({"n": n, "edges": [list(e) for e in edges]})
    return graphs


def test_all():
    graphs = generate_graphs(4, max_vars=15)
    total = len(graphs)
    passed = 0
    for g in graphs:
        ThreeColoring.validate(g)
        red = reduce(g)
        OneInThreeSat.validate(red)
        src_ans = three_coloring_bruteforce(g)
        tgt_ans = one_in_three_bruteforce(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!', g, src_ans, tgt_ans)
            return False, total, passed
    return True, total, passed

if __name__ == '__main__':
    ok, total, passed = test_all()
    print('All tests passed?', ok, f'({passed}/{total})')
    import json
    verdict = {
        "verified": ok,
        "tests_run": total,
        "tests_passed": passed
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
