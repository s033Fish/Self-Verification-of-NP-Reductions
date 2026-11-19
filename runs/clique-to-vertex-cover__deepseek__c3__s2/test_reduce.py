import random

from problems import Clique, VertexCover, all_graphs
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(inst):
    global tests_run, tests_passed
    tests_run += 1
    red = reduce(inst)
    # The reduction must produce a valid target instance.
    VertexCover.validate(red)
    expected = Clique.is_yes(inst)
    got = VertexCover.is_yes(red)
    assert got == expected, (inst, red, expected, got)
    tests_passed += 1


# Exhaustive: every graph on 0..4 vertices, every k from -1 to n+1.
for n in range(5):
    for edges in all_graphs(n):
        for k in range(-1, n + 2):
            check({"n": n, "edges": edges, "k": k})

# Random instances, including k outside 0..n.
rng = random.Random(12345)
for _ in range(2000):
    inst = Clique.random_instance(rng, rng.randint(0, 8))
    check(inst)

# Targeted edge cases.
for inst in [
    {"n": 0, "edges": [], "k": 0},
    {"n": 0, "edges": [], "k": -3},
    {"n": 0, "edges": [], "k": 5},
    {"n": 1, "edges": [], "k": 1},
    {"n": 1, "edges": [], "k": 0},
    {"n": 1, "edges": [], "k": 2},
    {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3},
    {"n": 3, "edges": [], "k": 1},
    {"n": 4, "edges": [[0, 1], [1, 2]], "k": -100},
    {"n": 4, "edges": [[0, 1], [1, 2]], "k": 100},
]:
    check(inst)

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
