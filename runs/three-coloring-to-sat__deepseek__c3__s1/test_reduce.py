import random
import problems
from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(inst):
    global tests_run, tests_passed
    tests_run += 1
    out = reduce(inst)
    # Validate both the source and the produced target instance.
    SOURCE.validate(inst)
    TARGET.validate(out)
    expected = SOURCE.is_yes(inst)
    got = TARGET.is_yes(out)
    assert got == expected, (inst, out, expected, got)
    tests_passed += 1


# Exhaustive: all graphs on 0..5 vertices (n=5 -> 1024 graphs, n=6 -> 32768).
for inst in SOURCE.enumerate_instances(5):
    check(inst)

# Also exhaustively cover all graphs on 6 vertices.
for inst in SOURCE.enumerate_instances(6):
    check(inst)

# Random graphs of larger sizes.
rng = random.Random(12345)
for scale in range(0, 10):
    for _ in range(60):
        check(SOURCE.random_instance(rng, scale))

# Explicit edge cases.
check({"n": 0, "edges": []})
check({"n": 1, "edges": []})
check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})          # triangle: yes
check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]]})  # K4: no
check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]})          # C5: no
check({"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]]})  # C6: yes

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
