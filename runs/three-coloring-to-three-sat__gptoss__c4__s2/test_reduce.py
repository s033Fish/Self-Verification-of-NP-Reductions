import itertools, json, sys
from problems import ThreeColoring, ThreeSat
from reduce import reduce

def solve_three_coloring(instance):
    n = instance['n']
    edges = instance['edges']
    for assign in itertools.product(range(3), repeat=n):
        if all(assign[u] != assign[v] for u, v in edges):
            return True
    return False

def solve_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for vals in itertools.product([False, True], repeat=m):
        if all(any((vals[abs(lit)-1] if lit > 0 else not vals[abs(lit)-1]) for lit in clause) for clause in clauses):
            return True
    return False

def generate_graphs():
    """Yield all graphs with up to 3 vertices (always 3‑colorable) and a K4 (non‑colorable)."""
    for n in range(0, 4):  # 0,1,2,3 vertices
        vertices = list(range(n))
        possible_edges = [(i, j) for i in vertices for j in vertices if i < j]
        for mask in range(1 << len(possible_edges)):
            edges = []
            for idx, (u, v) in enumerate(possible_edges):
                if mask >> idx & 1:
                    edges.append([u, v])
            yield {'n': n, 'edges': edges}
    # K4 (4 vertices, complete graph) – known to be not 3‑colorable
    yield {'n': 4, 'edges': [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]}

if __name__ == '__main__':
    total = 0
    passed = 0
    for instance in generate_graphs():
        total += 1
        ThreeColoring.validate(instance)
        ans_col = solve_three_coloring(instance)
        red = reduce(instance)
        ThreeSat.validate(red)
        ans_sat = solve_three_sat(red)
        if ans_col == ans_sat:
            passed += 1
        else:
            print('Mismatch', instance, ans_col, ans_sat, file=sys.stderr)
            break
    verdict = {'verified': passed == total, 'tests_run': total, 'tests_passed': passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))
