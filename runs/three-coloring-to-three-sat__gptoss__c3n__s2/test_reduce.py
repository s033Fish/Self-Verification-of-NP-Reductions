import random
import itertools
import json
from problems import ThreeColoring, ThreeSat
from reduce import reduce


def three_coloring_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    # iterate over all assignments of colors 0,1,2
    for colors in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colors[u] == colors[v]:
                ok = False
                break
        if ok:
            return True
    return False


def three_sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for vals in itertools.product([False, True], repeat=m):
        assignment = {i+1: vals[i] for i in range(m)}
        good = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit)
                sign = lit > 0
                if assignment[var] == sign:
                    clause_ok = True
                    break
            if not clause_ok:
                good = False
                break
        if good:
            return True
    return False


def generate_random_graph(max_n=5, edge_prob=0.5):
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def test_random_instances(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        inst = generate_random_graph()
        # validate source
        ThreeColoring.validate(inst)
        src_ans = three_coloring_bruteforce(inst)
        red = reduce(inst)
        ThreeSat.validate(red)
        tgt_ans = three_sat_bruteforce(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('Source:', inst)
            print('Reduced:', red)
            print('src_ans', src_ans, 'tgt_ans', tgt_ans)
            break
    return passed, num_tests


def test_edge_cases():
    # n=0
    inst0 = {"n": 0, "edges": []}
    assert three_coloring_bruteforce(inst0) == True
    red0 = reduce(inst0)
    assert three_sat_bruteforce(red0) == True
    # n<=3 any graph should be yes
    for n in range(1,4):
        # all possible edges
        all_edges = []
        for u in range(n):
            for v in range(u+1, n):
                all_edges.append([u,v])
        # test a few subsets
        for mask in range(1<<len(all_edges)):
            edges = [all_edges[i] for i in range(len(all_edges)) if (mask>>i)&1]
            inst = {"n": n, "edges": edges}
            assert three_coloring_bruteforce(inst) == True
            red = reduce(inst)
            assert three_sat_bruteforce(red) == True
    # K4 should be no
    n=4
    edges = []
    for u in range(n):
        for v in range(u+1,n):
            edges.append([u,v])
    k4 = {"n":4, "edges": edges}
    assert three_coloring_bruteforce(k4) == False
    redk4 = reduce(k4)
    assert three_sat_bruteforce(redk4) == False

if __name__ == '__main__':
    passed, total = test_random_instances(200)
    print(f'Random tests passed: {passed}/{total}')
    test_edge_cases()
    print('Edge case tests passed')
    # write verdict
    verdict = {
        "verified": passed == total,
        "tests_run": total +  (1 if True else 0),  # placeholder
        "tests_passed": passed + (1 if True else 0)
    }
    # adjust counts: edge case tests count as additional tests
    verdict["tests_run"] = total + 1  # edge cases as one big test
    verdict["tests_passed"] = passed + 1 if passed == total else passed
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('Verdict written')
