"""Tests for reduce.py: compare brute-force solvers on small instances."""
import random
import sys

sys.path.insert(0, ".")
from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    if expected == got:
        tests_passed += 1
    else:
        print("FAIL", instance, "->", reduced, "expected", expected, "got", got)


# --- Explicit edge cases ---------------------------------------------------
check({"num_vars": 0, "clauses": []})
check({"num_vars": 1, "clauses": []})
check({"num_vars": 2, "clauses": []})
check({"num_vars": 3, "clauses": []})
check({"num_vars": 5, "clauses": []})
check({"num_vars": 3, "clauses": [[1, 2, 3]]})
check({"num_vars": 3, "clauses": [[-1, -2, -3]]})
check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
# Duplicate clauses.
check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [3, 2, 1]]})
# Variables that never appear.
check({"num_vars": 6, "clauses": [[1, 2, 3]]})
# All 8 clauses over 3 variables: unsatisfiable.
check({"num_vars": 3, "clauses": [
    [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
    [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3]]})

# --- Exhaustive over all formulas with num_vars <= 3 -----------------------
for instance in SOURCE.enumerate_instances(3):
    check(instance)

# --- Random instances ------------------------------------------------------
rng = random.Random(123456)
for scale in range(0, 9):
    for _ in range(400):
        check(SOURCE.random_instance(rng, scale))

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed, "some tests failed"
