import json
import random
import sys

from problems import SOURCE, TARGET
from reduce import reduce

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    if expected == got:
        TESTS_PASSED += 1
        return True
    print("FAIL")
    print("  source:", json.dumps(instance))
    print("  reduced:", json.dumps(reduced))
    print("  expected", expected, "got", got)
    return False


def main():
    ok = True

    # Edge cases: no clauses for many m, including m = 0.
    for m in range(0, 8):
        ok &= check({"num_vars": m, "clauses": []})

    # Exhaustive small formulas: all distinct clauses over 3 variables.
    from itertools import combinations, product
    all_clauses = [
        [sign * v for sign, v in zip(signs, variables)]
        for variables in combinations(range(1, 4), 3)
        for signs in product((1, -1), repeat=3)
    ]
    for mask in range(1 << len(all_clauses)):
        instance = {
            "num_vars": 3,
            "clauses": [c for i, c in enumerate(all_clauses) if mask >> i & 1],
        }
        ok &= check(instance)

    # Random formulas of several sizes, including duplicates and unused vars.
    rng = random.Random(12345)
    for _ in range(400):
        m = rng.randint(0, 7)
        if m < 3:
            clauses = []
        else:
            clauses = []
            for _ in range(rng.randint(0, 12)):
                variables = rng.sample(range(1, m + 1), 3)
                clauses.append(
                    [v if rng.random() < 0.5 else -v for v in sorted(variables)]
                )
        ok &= check({"num_vars": m, "clauses": clauses})

    # Use the problem's own generator too.
    for scale in range(0, 7):
        for _ in range(60):
            ok &= check(SOURCE.random_instance(rng, scale))

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    verdict = {
        "verified": bool(ok and TESTS_RUN == TESTS_PASSED),
        "tests_run": TESTS_RUN,
        "tests_passed": TESTS_PASSED,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print(json.dumps(verdict))
    return 0 if verdict["verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
