import random
from itertools import combinations, product

import problems
from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    out = reduce(instance)
    TARGET.validate(out)  # reduction must produce a valid target instance
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(out)
    assert got == expected, (instance, out, expected, got)
    tests_passed += 1


# 1. Exhaustive: every formula with num_vars <= 3 and distinct clauses.
for instance in SOURCE.enumerate_instances(3):
    check(instance)

# 2. Explicit edge cases.
check({"num_vars": 0, "clauses": []})
check({"num_vars": 5, "clauses": []})
check({"num_vars": 3, "clauses": [[1, 2, 3]]})
check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]})
check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3],
                                  [1, -2, 3], [-1, 2, -3],
                                  [1, 2, -3], [-1, -2, 3],
                                  [1, -2, -3], [-1, 2, 3]]})

# 3. Random small formulas: keep clause count small so the exponential
#    independent-set solver stays fast.
rng = random.Random(12345)
for scale in range(3, 7):
    for _ in range(40):
        n_clauses = rng.randint(0, 8)
        clauses = []
        for _ in range(n_clauses):
            variables = rng.sample(range(1, scale + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in sorted(variables)])
        check({"num_vars": scale, "clauses": clauses})

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
