import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    out = reduce(instance)
    TARGET.validate(out)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(out)
    assert expected == got, (
        f"mismatch for {instance}: source={expected}, target={got}, reduced={out}"
    )
    tests_passed += 1


# Edge case: no clauses, including m = 0.
for m in range(0, 8):
    check({"num_vars": m, "clauses": []})

# Exhaustive: all formulas with m <= 3 and at most 4 distinct clauses.
for m in range(0, 4):
    all_clauses = [
        [sign * v for sign, v in zip(signs, variables)]
        for variables in itertools.combinations(range(1, m + 1), 3)
        for signs in itertools.product((1, -1), repeat=3)
    ]
    for r in range(0, min(4, len(all_clauses)) + 1):
        for subset in itertools.combinations(all_clauses, r):
            check({"num_vars": m, "clauses": [list(c) for c in subset]})

# Random small instances: keep the reduced graph small (n <= 24) so the
# brute-force Independent Set solver stays fast.
rng = random.Random(12345)
for _ in range(6000):
    m = rng.randint(3, 6)
    n_clauses = rng.randint(0, 8)
    clauses = []
    for _ in range(n_clauses):
        variables = rng.sample(range(1, m + 1), 3)
        clauses.append([v if rng.random() < 0.5 else -v for v in variables])
    check({"num_vars": m, "clauses": clauses})

# Duplicate clauses and unused variables.
for _ in range(1000):
    m = rng.randint(3, 6)
    base = []
    for _ in range(rng.randint(1, 3)):
        variables = rng.sample(range(1, m + 1), 3)
        base.append([v if rng.random() < 0.5 else -v for v in variables])
    clauses = [list(c) for c in base for _ in range(rng.randint(1, 3))]
    check({"num_vars": m, "clauses": clauses})

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
