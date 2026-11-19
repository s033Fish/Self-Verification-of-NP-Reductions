"""Tests for reduce.py: compare solver answers on many small instances."""
import random

from problems import VertexCover, Sat
from reduce import reduce
from solvers import solve_vertex_cover, solve_sat, solve_sat_brute

tests_run = 0
tests_passed = 0


def check(instance, brute=False):
    global tests_run, tests_passed
    tests_run += 1
    VertexCover.validate(instance)
    out = reduce(instance)
    Sat.validate(out)
    expected = solve_vertex_cover(instance)
    got = solve_sat(out)
    if brute:
        assert solve_sat_brute(out) == got, "DPLL disagrees with brute force"
    assert got == expected, (
        f"MISMATCH src={instance} -> tgt={out} expected={expected} got={got}"
    )
    tests_passed += 1


def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if (mask >> i) & 1]
        yield edges


def main():
    # Exhaustive over all graphs on n <= 4 vertices, all k in a range.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k}, brute=True)

    # Random small instances, including sparse/dense and varied k.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 6)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(p) for p in pairs if rng.random() < rng.choice([0.2, 0.5, 0.9])]
        rng.shuffle(edges)
        for e in edges:
            if rng.random() < 0.5:
                e.reverse()
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})

    # Larger random instances (DPLL handles the auxiliary variables).
    for _ in range(300):
        n = rng.randint(8, 14)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(p) for p in pairs if rng.random() < rng.choice([0.15, 0.4, 0.8])]
        k = rng.randint(-1, n + 1)
        check({"n": n, "edges": edges, "k": k})

    # Targeted edge cases.
    for inst in [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -1},
        {"n": 0, "edges": [], "k": 5},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": -1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
        {"n": 5, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 5, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 1, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": -1},
    ]:
        check(inst, brute=True)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()


def test_isolated():
    """Many isolated vertices must not inflate the output."""
    global tests_run, tests_passed
    for n, edges, k in [
        (1000, [[0, 1], [2, 3]], 1),
        (1000, [[0, 1], [2, 3]], 2),
        (1000, [], 0),
        (1000, [], -1),
        (1000, [[0, 1]], 500),
    ]:
        inst = {"n": n, "edges": edges, "k": k}
        tests_run += 1
        VertexCover.validate(inst)
        out = reduce(inst)
        Sat.validate(out)
        assert out["num_vars"] <= 20, out["num_vars"]
        assert solve_vertex_cover(inst) == solve_sat(out)
        tests_passed += 1
    print(f"after isolated: tests_run={tests_run} tests_passed={tests_passed}")


test_isolated()
