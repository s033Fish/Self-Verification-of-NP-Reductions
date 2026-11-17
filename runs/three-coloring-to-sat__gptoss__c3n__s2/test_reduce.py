import itertools, json, random, sys
from problems import ThreeColoring, Sat
from reduce import reduce

def three_coloring_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    # Edge case n=0 always yes
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False

def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for assign in itertools.product([False, True], repeat=m):
        # assign is tuple index 0..m-1
        good = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                good = False
                break
        if good:
            return True
    return False

def test_random_graphs(num_tests=200):
    for _ in range(num_tests):
        n = random.randint(0, 5)  # small for brute force
        # generate random edges without duplicates
        possible = [(i, j) for i in range(n) for j in range(i+1, n)]
        edges = []
        for (i, j) in possible:
            if random.random() < 0.3:
                edges.append([i, j])
        instance = {'n': n, 'edges': edges}
        ThreeColoring.validate(instance)
        sat_instance = reduce(instance)
        # compare answers
        ans1 = three_coloring_bruteforce(instance)
        ans2 = sat_bruteforce(sat_instance)
        if ans1 != ans2:
            print('Mismatch!', instance, ans1, ans2)
            return False
    return True

def test_edge_cases():
    # n=0
    inst0 = {'n':0, 'edges':[]}
    assert three_coloring_bruteforce(inst0) == True
    assert sat_bruteforce(reduce(inst0)) == True
    # n<=3 always yes
    for n in range(1,4):
        # all possible edges
        edges = []
        for i in range(n):
            for j in range(i+1, n):
                edges.append([i,j])
        inst = {'n':n, 'edges':edges}
        assert three_coloring_bruteforce(inst) == True
        assert sat_bruteforce(reduce(inst)) == True
    # K4 should be no
    n=4
    edges = [[i,j] for i in range(4) for j in range(i+1,4)]
    k4 = {'n':4, 'edges':edges}
    assert three_coloring_bruteforce(k4) == False
    assert sat_bruteforce(reduce(k4)) == False
    return True

if __name__ == '__main__':
    ok = True
    ok &= test_edge_cases()
    ok &= test_random_graphs(300)
    result = {
        'verified': ok,
        'tests_run': 1 + 300,
        'tests_passed': (1 if ok else 0)
    }
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
    print('All tests passed' if ok else 'Some tests failed')
    sys.exit(0 if ok else 1)
