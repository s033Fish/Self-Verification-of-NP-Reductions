"""Tests for reduce.py: compare brute-force answers on many small instances.

The reduction is checked by running the exact solvers from problems.py on the
source instance and on the reduced 3-Coloring instance and asserting that the
two answers agree.  Instances are kept small enough that the exponential
brute-force 3-colouring search terminates quickly.
"""

import random
import sys
import time

from problems import NaeThreeSat, ThreeColoring
from reduce import reduce

sys.setrecursionlimit(100000)

tests_run = 0
tests_passed = 0
start = time.time()


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    NaeThreeSat.validate(instance)
    target = reduce(instance)
    ThreeColoring.validate(target)
    expected = NaeThreeSat.is_yes(instance)
    got = ThreeColoring.is_yes(target)
    if expected != got:
        print("MISMATCH")
        print("source:", instance)
        print("expected:", expected, "got:", got)
        print("target:", target)
        raise SystemExit(1)
    tests_passed += 1


# 1. Exhaustive over every formula with num_vars <= 3 (259 formulas).
for scale in range(0, 4):
    count = 0
    for instance in NaeThreeSat.enumerate_instances(scale):
        check(instance)
        count += 1
    print(f"enumerated scale {scale}: {count} instances, {time.time()-start:.1f}s")

# 2. Random instances from the problem's own generator, small scales only
#    (its larger scales create too many clauses for the brute-force solver).
rng = random.Random(12345)
for scale in range(0, 4):
    for _ in range(40):
        check(NaeThreeSat.random_instance(rng, scale))
print(f"random done, {time.time()-start:.1f}s")

# 3. Hand-picked edge cases, including the documented ones.
edge_cases = [
    {"num_vars": 0, "clauses": []},                       # no clauses, m=0
    {"num_vars": 1, "clauses": []},                       # no clauses, m<3
    {"num_vars": 2, "clauses": []},
    {"num_vars": 3, "clauses": []},
    {"num_vars": 10, "clauses": []},                      # many unused vars
    {"num_vars": 3, "clauses": [[1, 2, 3]]},              # all-true is bad
    {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},   # duplicate clause
    {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},  # unsat
    {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, 2, -3]]},
    {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]},
    {"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, 3], [1, -2, -3], [-1, 2, -3]]},
    {"num_vars": 5, "clauses": [[1, 2, 3], [3, 4, 5], [-1, -2, -3], [-3, -4, -5]]},
    {"num_vars": 6, "clauses": [[1, 2, 3], [-1, -2, -3], [4, 5, 6], [-4, -5, -6]]},
]
for instance in edge_cases:
    check(instance)
print(f"edge cases done, {time.time()-start:.1f}s")

# 4. Random instances biased toward unsatisfiable (all-positive clauses).
rng = random.Random(999)
for _ in range(200):
    m = rng.randint(3, 5)
    clauses = []
    for _ in range(rng.randint(1, 6)):
        clauses.append(rng.sample(range(1, m + 1), 3))
    check({"num_vars": m, "clauses": clauses})

# 5. Random instances biased toward satisfiable (mixed signs).
rng = random.Random(4242)
for _ in range(200):
    m = rng.randint(3, 5)
    clauses = []
    for _ in range(rng.randint(1, 6)):
        vs = rng.sample(range(1, m + 1), 3)
        clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    check({"num_vars": m, "clauses": clauses})

# 6. Structured instances with a known answer.
#    Clauses [v, w, x] and [-v, -w, -x] force each triple to be mixed.
rng = random.Random(2024)
for _ in range(100):
    m = rng.randint(3, 6)
    clauses = []
    for _ in range(rng.randint(1, 4)):
        vs = rng.sample(range(1, m + 1), 3)
        clauses.append(list(vs))
        clauses.append([-v for v in vs])
    check({"num_vars": m, "clauses": clauses})

# 7. Structural sanity: reduction is polynomial in size.
big = {"num_vars": 200, "clauses": [[1, 2, 3]] * 500}
t0 = time.time()
out = reduce(big)
elapsed = time.time() - t0
ThreeColoring.validate(out)
assert out["n"] == 3 + 2 * 200 + 3 * 500
assert elapsed < 5.0, f"reduction too slow: {elapsed}s"
print(f"big reduction: n={out['n']} edges={len(out['edges'])} in {elapsed:.3f}s")

print(f"tests_run={tests_run} tests_passed={tests_passed} time={time.time()-start:.1f}s")
assert tests_run == tests_passed
print("ALL TESTS PASSED")
