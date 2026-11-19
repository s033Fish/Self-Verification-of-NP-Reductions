import itertools
import random
from problems import ThreeColoring, ThreeSat
from reduce import reduce


def solve_three_coloring(instance):
    n = instance['n']
    edges = [tuple(e) for e in instance['edges']]
    for coloring in itertools.product(range(3), repeat=n):
        if all(coloring[u] != coloring[v] for u, v in edges):
            return True
    return False


def solve_three_sat(instance):
    m = instance['num_vars']
    clauses = [tuple(c) for c in instance['clauses']]
    for assignment in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((lit > 0 and assignment[abs(lit)-1]) or (lit < 0 and not assignment[abs(lit)-1]) for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def random_graph(n, p=0.5):
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}

def test_all_small_graphs(max_n=3):
    total = 0
    passed = 0
    for n in range(max_n+1):
        vertices = list(range(n))
        all_pairs = [(u, v) for u in vertices for v in vertices if u < v]
        for mask in range(1 << len(all_pairs)):
            edges = []
            for i, (u, v) in enumerate(all_pairs):
                if mask & (1 << i):
                    edges.append([u, v])
            instance = {"n": n, "edges": edges}
            ThreeColoring.validate(instance)
            red = reduce(instance)
            ThreeSat.validate(red)
            ans1 = solve_three_coloring(instance)
            ans2 = solve_three_sat(red)
            total += 1
            if ans1 == ans2:
                passed += 1
            else:
                print("Mismatch!", instance, ans1, ans2)
                return False, total, passed
    return True, total, passed

if __name__ == "__main__":
    ok, total, passed = test_all_small_graphs(3)
    print("All tests passed?", ok, "tested", total, "instances, passed", passed)
    # Random tests – keep n small to keep SAT brute‑force feasible.
    for _ in range(30):
        n = random.randint(0, 2)
        inst = random_graph(n, 0.4)
        ThreeColoring.validate(inst)
        red = reduce(inst)
        ThreeSat.validate(red)
        assert solve_three_coloring(inst) == solve_three_sat(red)
    print("Random tests passed")
