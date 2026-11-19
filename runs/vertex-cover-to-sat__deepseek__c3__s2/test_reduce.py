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
    target = reduce(instance)
    Sat.validate(target)  # reduction must produce a valid SAT instance
    expected = VertexCover.is_yes(instance)
    got = Sat.is_yes(target)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH", instance, "expected", expected, "got", got, "target", target)


# Exhaustive over all small graphs with every k from -1 to n+1.
for scale in range(5):
    for instance in VertexCover.enumerate_instances(scale):
        check(instance)

# Random larger instances.
rng = random.Random(12345)
for _ in range(3000):
    scale = rng.randint(0, 8)
    check(VertexCover.random_instance(rng, scale))

# Targeted edge cases.
edge_cases = [
    {"n": 0, "edges": [], "k": -1},
    {"n": 0, "edges": [], "k": 0},
    {"n": 0, "edges": [], "k": 5},
    {"n": 3, "edges": [], "k": -1},
    {"n": 3, "edges": [], "k": 0},
    {"n": 3, "edges": [], "k": 2},
    {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},
    {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 1},
    {"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]], "k": 1},
    {"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]], "k": 0},
    {"n": 6, "edges": [[i, j] for i in range(6) for j in range(i + 1, 6)], "k": 5},
    {"n": 6, "edges": [[i, j] for i in range(6) for j in range(i + 1, 6)], "k": 4},
    {"n": 2, "edges": [[0, 1]], "k": 100},
]
for instance in edge_cases:
    check(instance)

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed, "some tests failed"
