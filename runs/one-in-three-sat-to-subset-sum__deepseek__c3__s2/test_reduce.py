import random
import sys

from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    TARGET.validate(instance) if False else None
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    if expected == got:
        tests_passed += 1
        return True
    print("MISMATCH")
    print("  source:", instance)
    print("  expected:", expected, "got:", got)
    print("  reduced:", reduced)
    return False


def main():
    ok = True

    # Edge cases
    ok &= check({"num_vars": 0, "clauses": []})
    ok &= check({"num_vars": 5, "clauses": []})
    ok &= check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    ok &= check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    ok &= check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3]]})
    ok &= check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]})
    ok &= check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [3, 4, 1]]})
    ok &= check({"num_vars": 6, "clauses": [[1, 2, 3], [4, 5, 6]]})

    # Exhaustive small formulas
    for scale in range(0, 6):
        count = 0
        for inst in SOURCE.enumerate_instances(scale):
            ok &= check(inst)
            count += 1
            if count > 20000:
                break
        print(f"scale {scale}: {count} instances")

    # Random instances
    rng = random.Random(12345)
    for scale in range(3, 12):
        for _ in range(400):
            inst = SOURCE.random_instance(rng, scale)
            ok &= check(inst)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
