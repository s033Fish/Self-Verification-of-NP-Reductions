"""Tests for reduce.py: compare brute-force SAT vs Independent Set answers."""
import random
import itertools

import problems
from problems import Sat, IndependentSet
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    Sat.validate(instance)
    target = reduce(instance)
    IndependentSet.validate(target)  # must be a valid target instance
    src = Sat.is_yes(instance)
    dst = IndependentSet.is_yes(target)
    if src != dst:
        raise AssertionError(
            f"MISMATCH src={src} dst={dst}\ninstance={instance}\nreduced={target}"
        )
    tests_passed += 1


# 1. Exhaustive enumeration of small SAT instances.
for scale in range(3):
    for inst in Sat.enumerate_instances(scale):
        check(inst)

# 2. Random instances from the provided generator.
rng = random.Random(12345)
for scale in range(0, 7):
    for _ in range(300):
        check(Sat.random_instance(rng, scale))

# 3. Hand-crafted edge cases: empty formula, empty clauses, repeats,
#    complementary literals, unused variables.
edge_cases = [
    {"num_vars": 0, "clauses": []},
    {"num_vars": 0, "clauses": [[]]},
    {"num_vars": 1, "clauses": []},
    {"num_vars": 1, "clauses": [[]]},
    {"num_vars": 1, "clauses": [[1]]},
    {"num_vars": 1, "clauses": [[-1]]},
    {"num_vars": 1, "clauses": [[1], [-1]]},
    {"num_vars": 1, "clauses": [[1, -1]]},
    {"num_vars": 1, "clauses": [[1, 1]]},
    {"num_vars": 1, "clauses": [[-1, -1]]},
    {"num_vars": 2, "clauses": [[1, 2], [-1, -2], [1, -2], [-1, 2]]},
    {"num_vars": 2, "clauses": [[1], [2], [-1, -2]]},
    {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], []]},
    {"num_vars": 3, "clauses": [[1, 2], [2, 3], [1, 3], [-1, -2, -3]]},
    {"num_vars": 4, "clauses": [[1, -1], [2, -2], [3, -3], [4, -4]]},
    {"num_vars": 5, "clauses": [[i] for i in range(1, 6)]},
    {"num_vars": 5, "clauses": [[-i] for i in range(1, 6)]},
    {"num_vars": 5, "clauses": [[i, -i] for i in range(1, 6)]},
    {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
]
for inst in edge_cases:
    check(inst)

# 4. Random instances with repeats / empty clauses / complementary literals.
rng = random.Random(999)
for _ in range(2000):
    m = rng.randint(0, 5)
    nclauses = rng.randint(0, 8)
    clauses = []
    for _ in range(nclauses):
        length = rng.randint(0, 5)
        clause = []
        for _ in range(length):
            if m == 0:
                break
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    check({"num_vars": m, "clauses": clauses})

# 5. Polynomial-size sanity: reduction output size is bounded.
big = {"num_vars": 50, "clauses": [[(i % 50) + 1, -((i % 50) + 1)] for i in range(200)]}
big_target = reduce(big)
assert big_target["n"] == 400
assert big_target["k"] == 200

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
