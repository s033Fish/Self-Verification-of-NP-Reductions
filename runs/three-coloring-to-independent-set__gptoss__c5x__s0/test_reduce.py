"""Independent checks of reduce.py: brute-force solvers + exhaustive/random tests."""
import itertools
import random

from problems import ThreeColoring, IndependentSet
from reduce import reduce


# ---------------- brute-force solvers from the definitions ----------------

def solve_three_coloring(inst):
    n = inst["n"]
    edges = inst["edges"]
    for colours in itertools.product(range(3), repeat=n):
        if all(colours[u] != colours[v] for u, v in edges):
            return True
    return False


def solve_independent_set(inst):
    n = inst["n"]
    edges = inst["edges"]
    k = inst["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    best = 0

    def rec(candidates, count):
        nonlocal best
        if count + bin(candidates).count("1") <= best:
            return
        if candidates == 0:
            best = max(best, count)
            return
        v = (candidates & -candidates).bit_length() - 1
        rec(candidates & ~adj[v] & ~(1 << v), count + 1)
        rec(candidates & ~(1 << v), count)

    rec((1 << n) - 1, 0)
    return best >= k


# ---------------- helpers ----------------

def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


tests_run = 0
tests_passed = 0
failures = []


def check(inst, label):
    global tests_run, tests_passed
    tests_run += 1
    try:
        src = solve_three_coloring(inst)
        red = reduce(inst)
        IndependentSet.validate(red)  # target must be well-formed
        tgt = solve_independent_set(red)
        assert src == tgt, f"mismatch src={src} tgt={tgt} red={red}"
        tests_passed += 1
    except Exception as exc:  # noqa: BLE001
        failures.append((label, inst, repr(exc)))


# 1) exhaustive over all graphs with n = 0..4
for n in range(0, 5):
    for inst in all_graphs(n):
        check(inst, f"exhaustive n={n}")

# 2) random graphs n = 5..8
rng = random.Random(12345)
for n in range(5, 9):
    for _ in range(300):
        p = rng.choice([0.0, 0.15, 0.3, 0.5, 0.7, 1.0])
        check(random_graph(n, p, rng), f"random n={n} p={p}")

# 3) explicit edge cases
check({"n": 0, "edges": []}, "n=0")
check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, "K3")
check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}, "K4")
check({"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}, "K4+isolated")

print(f"tests_run={tests_run} tests_passed={tests_passed}")
if failures:
    print("FAILURES:")
    for label, inst, err in failures[:10]:
        print(" ", label, inst, err)
else:
    print("ALL TESTS PASSED")
