import random
import time

from problems import SubsetSum, Sat
from reduce import reduce

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    SubsetSum.validate(instance)
    out = reduce(instance)
    Sat.validate(out)
    expected = SubsetSum.is_yes(instance)
    got = Sat.is_yes(out)
    if expected == got:
        TESTS_PASSED += 1
    else:
        print("MISMATCH", instance, "expected", expected, "got", got)
        raise SystemExit(1)


# 1. Exhaustive small instances from the problem's own enumerator.
count = 0
for instance in SubsetSum.enumerate_instances(4):
    check(instance)
    count += 1
print("enumerated instances checked:", count)

# 2. Random instances at several scales (kept small enough for the
#    pure-Python DPLL fallback to finish quickly).
rng = random.Random(12345)
for scale in range(0, 7):
    for _ in range(120):
        check(SubsetSum.random_instance(rng, scale))
print("random instances checked")

# 3. Hand-picked edge cases, including huge values and exact boundaries.
edge = [
    {"numbers": [], "target": 0},
    {"numbers": [], "target": 1},
    {"numbers": [], "target": -1},
    {"numbers": [0], "target": 0},
    {"numbers": [0, 0, 0], "target": 0},
    {"numbers": [0, 0, 0], "target": 1},
    {"numbers": [5], "target": 5},
    {"numbers": [5], "target": 0},
    {"numbers": [5], "target": 6},
    {"numbers": [1, 1, 1, 1], "target": 3},
    {"numbers": [2, 2, 2], "target": 5},
    {"numbers": [10 ** 18, 1], "target": 10 ** 18},
    {"numbers": [10 ** 18, 1], "target": 10 ** 18 + 1},
    {"numbers": [10 ** 18, 1], "target": 10 ** 18 + 2},
    {"numbers": [2 ** 40, 2 ** 40 - 1], "target": 2 ** 41 - 1},
    {"numbers": [7, 7, 7, 7, 7], "target": 21},
    {"numbers": [7, 7, 7, 7, 7], "target": 22},
    {"numbers": [1, 2, 4, 8, 16], "target": 31},
    {"numbers": [1, 2, 4, 8, 16], "target": 30},
    {"numbers": [3, 0, 3, 0], "target": 6},
    {"numbers": [100, 200, 300], "target": 500},
    {"numbers": [100, 200, 300], "target": 600},
    {"numbers": [100, 200, 300], "target": 601},
    {"numbers": [0, 0, 0, 0], "target": 0},
    {"numbers": [1, 0, 1, 0], "target": 2},
]
for instance in edge:
    check(instance)
print("edge cases checked")

# 4. Larger random instances (still brute-forceable).
for _ in range(60):
    n = rng.randint(1, 10)
    numbers = [rng.randint(0, 200) for _ in range(n)]
    total = sum(numbers)
    target = rng.choice([
        rng.randint(0, total + 2),
        -rng.randint(0, 10),
        total + rng.randint(0, 5),
    ])
    check({"numbers": numbers, "target": target})
print("larger random instances checked")

# 5. Verify the reduction is polynomial-ish: a moderately large input
#    (many numbers, large values) must reduce quickly.
big = {"numbers": [rng.randint(1, 10 ** 12) for _ in range(300)], "target": 123456789}
t0 = time.time()
out = reduce(big)
elapsed = time.time() - t0
Sat.validate(out)
print("large input reduced in %.3fs to %d vars / %d clauses"
      % (elapsed, out["num_vars"], len(out["clauses"])))
assert elapsed < 10.0

print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
assert TESTS_RUN == TESTS_PASSED

# 6. Independent brute-force cross-check (enumerate all subsets and all
#    assignments) rather than trusting the bundled solvers.
import itertools


def brute_subset_sum(numbers, target):
    if target < 0:
        return False
    n = len(numbers)
    for mask in range(1 << n):
        if sum(numbers[i] for i in range(n) if mask >> i & 1) == target:
            return True
    return False


def brute_sat(inst):
    m = inst["num_vars"]
    clauses = inst["clauses"]
    if any(not c for c in clauses):
        return False
    for bits in itertools.product([False, True], repeat=m):
        if all(any((lit > 0) == bits[abs(lit) - 1] for lit in c) for c in clauses):
            return True
    return False


rng2 = random.Random(999)
ind = 0
for _ in range(4000):
    n = rng2.randint(0, 5)
    numbers = [rng2.randint(0, 6) for _ in range(n)]
    total = sum(numbers)
    target = rng2.choice([rng2.randint(-2, total + 2), total, total + 1, 0])
    instance = {"numbers": numbers, "target": target}
    out = reduce(instance)
    if out["num_vars"] > 18:
        continue
    TESTS_RUN += 1
    if brute_subset_sum(numbers, target) == brute_sat(out):
        TESTS_PASSED += 1
    else:
        print("INDEPENDENT MISMATCH", instance)
        raise SystemExit(1)
    ind += 1
print("independent brute-force checks passed:", ind)

print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
assert TESTS_RUN == TESTS_PASSED
