import itertools
import random

import problems
from problems import VertexCover, Sat
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    VertexCover.validate(instance)
    out = reduce(instance)
    Sat.validate(out)
    expected = VertexCover.is_yes(instance)
    got = Sat.is_yes(out)
    assert got == expected, (
        f"MISMATCH on {instance}: source={expected}, reduced={got}, out={out}"
    )
    tests_passed += 1


# 1) Exhaustive small graphs, all k in -1..n+1
for n in range(0, 5):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        for k in range(-1, n + 2):
            check({"n": n, "edges": edges, "k": k})

# 2) n=5 exhaustive graphs with a few k values (2^10 graphs)
n = 5
pairs = list(itertools.combinations(range(n), 2))
for mask in range(1 << len(pairs)):
    edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
    for k in (-1, 0, 1, 2, 3, 4, 5, 6):
        check({"n": n, "edges": edges, "k": k})

# 3) Random larger instances
rng = random.Random(12345)
for _ in range(3000):
    inst = VertexCover.random_instance(rng, rng.randint(0, 9))
    check(inst)

# 4) Random instances with explicit extreme k
for _ in range(2000):
    n = rng.randint(0, 9)
    edges = problems.random_graph(rng, n)
    k = rng.choice([-5, -1, 0, 1, n - 1, n, n + 1, n + 50])
    check({"n": n, "edges": edges, "k": k})

# 5) Complete graphs and empty graphs
for n in range(0, 12):
    complete = [[u, v] for u, v in itertools.combinations(range(n), 2)]
    for k in range(-1, n + 2):
        check({"n": n, "edges": complete, "k": k})
        check({"n": n, "edges": [], "k": k})

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed

# 6) Larger random graphs (brute force still feasible)
for _ in range(1500):
    inst = VertexCover.random_instance(rng, rng.randint(10, 14))
    check(inst)

# 7) Dense/sparse larger graphs with boundary k
for _ in range(1000):
    n = rng.randint(10, 14)
    p = rng.choice([0.0, 0.1, 0.3, 0.5, 0.9, 1.0])
    edges = problems.random_graph(rng, n, p)
    k = rng.choice([-1, 0, 1, n // 2, n - 1, n, n + 3])
    check({"n": n, "edges": edges, "k": k})

print(f"final tests_run={tests_run} tests_passed={tests_passed}")
