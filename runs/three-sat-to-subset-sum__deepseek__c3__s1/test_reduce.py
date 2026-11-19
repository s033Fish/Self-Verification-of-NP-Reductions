import itertools
import random

import problems
from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    out = reduce(instance)
    TARGET.validate(out)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(out)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH", label, instance, "->", out, "expected", expected, "got", got)
    return expected == got


def all_small_formulas(max_vars=3):
    """Enumerate formulas with <= max_vars variables, distinct clauses."""
    for num_vars in range(max_vars + 1):
        all_clauses = [
            [s * v for s, v in zip(signs, variables)]
            for variables in itertools.combinations(range(1, num_vars + 1), 3)
            for signs in itertools.product((1, -1), repeat=3)
        ]
        for mask in range(1 << len(all_clauses)):
            clauses = [c for i, c in enumerate(all_clauses) if mask >> i & 1]
            yield {"num_vars": num_vars, "clauses": clauses}


def main():
    # Edge cases explicitly.
    check({"num_vars": 0, "clauses": []}, "m=0 no clauses")
    check({"num_vars": 5, "clauses": []}, "m=5 no clauses")
    # A single clause, satisfiable.
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "one clause")
    # Unsatisfiable: all 8 clauses over 3 vars.
    all8 = [
        [s * v for s, v in zip(signs, variables)]
        for variables in [tuple(range(1, 4))]
        for signs in itertools.product((1, -1), repeat=3)
    ]
    check({"num_vars": 3, "clauses": all8}, "all 8 clauses unsat")

    # Exhaustive small formulas with up to 3 variables.
    count = 0
    for inst in all_small_formulas(3):
        check(inst, "exhaustive")
        count += 1
    print("exhaustive formulas:", count)

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(300):
        scale = rng.randint(3, 8)
        check(SOURCE.random_instance(rng, scale), "random")

    # Duplicate clauses and clauses not covering all variables.
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 3], [-1, -2, -3]]}, "dupes")
    check({"num_vars": 6, "clauses": [[1, 2, 3], [4, 5, 6]]}, "unused vars")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    run, passed = main()
    assert run == passed, "some tests failed"
    print("ALL TESTS PASSED")
