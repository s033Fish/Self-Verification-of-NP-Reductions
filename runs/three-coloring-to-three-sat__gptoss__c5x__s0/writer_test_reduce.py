import random
import itertools
import json
from problems import ThreeColoring, ThreeSat
from reduce import reduce

def brute_three_coloring(instance):
    ThreeColoring.validate(instance)
    n = instance['n']
    edges = instance['edges']
    for assignment in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if assignment[u] == assignment[v]:
                ok = False
                break
        if ok:
            return True
    return False

def solve_three_sat(instance):
    """Simple backtracking SAT solver for 3‑SAT instances (small sizes)."""
    ThreeSat.validate(instance)
    m = instance['num_vars']
    clauses = [list(c) for c in instance['clauses']]
    assignment = [None] * m  # None, True, False

    def clause_satisfied(clause):
        for lit in clause:
            var = abs(lit) - 1
            val = assignment[var]
            if val is None:
                continue
            if (lit > 0 and val) or (lit < 0 and not val):
                return True
        return False

    def clause_conflict(clause):
        # all literals assigned and none true
        for lit in clause:
            var = abs(lit) - 1
            val = assignment[var]
            if val is None:
                return False
            if (lit > 0 and val) or (lit < 0 and not val):
                return False
        return True

    def unit_propagate():
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                if clause_satisfied(clause):
                    continue
                # collect unassigned literals
                unassigned = []
                for lit in clause:
                    var = abs(lit) - 1
                    if assignment[var] is None:
                        unassigned.append(lit)
                if not unassigned:
                    return False  # conflict
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    var = abs(lit) - 1
                    val = lit > 0
                    if assignment[var] is not None and assignment[var] != val:
                        return False
                    if assignment[var] is None:
                        assignment[var] = val
                        changed = True
        return True

    def backtrack(idx=0):
        # find next unassigned variable
        while idx < m and assignment[idx] is not None:
            idx += 1
        if idx == m:
            return all(clause_satisfied(c) for c in clauses)
        for val in (False, True):
            assignment[idx] = val
            saved = assignment.copy()
            if unit_propagate():
                if backtrack(idx + 1):
                    return True
            assignment[:] = saved
        assignment[idx] = None
        return False

    return backtrack()

def random_graph(max_n=5, edge_prob=0.4):
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {"n": n, "edges": edges}

def test_random(num_cases=200):
    for _ in range(num_cases):
        inst = random_graph()
        red = reduce(inst)
        ans_src = brute_three_coloring(inst)
        ans_tgt = solve_three_sat(red)
        if ans_src != ans_tgt:
            print('Mismatch!')
            print('src', inst)
            print('red', red)
            print('src ans', ans_src, 'tgt ans', ans_tgt)
            return False
    return True

def test_edge_cases():
    # n=0
    inst = {"n": 0, "edges": []}
    assert brute_three_coloring(inst) is True
    red = reduce(inst)
    assert solve_three_sat(red) is True
    # n<=3 always yes
    for n in range(1, 4):
        inst = {"n": n, "edges": []}
        assert brute_three_coloring(inst) is True
        assert solve_three_sat(reduce(inst)) is True
    # K4 should be no
    inst = {"n": 4, "edges": [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]}
    assert brute_three_coloring(inst) is False
    assert solve_three_sat(reduce(inst)) is False
    return True

if __name__ == '__main__':
    ok = test_edge_cases() and test_random(200)
    result = {"verified": ok, "tests_run": 1, "tests_passed": 1 if ok else 0}
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
    print('All tests passed' if ok else 'Tests failed')
