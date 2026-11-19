"""Tests for the 3-SAT -> NAE-3-SAT reduction."""
import random

import problems
from problems import ThreeSat, NaeThreeSat
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    # Source must be valid.
    ThreeSat.validate(instance)
    out = reduce(instance)
    # Output must be a valid NAE-3-SAT instance.
    NaeThreeSat.validate(out)
    expected = ThreeSat.is_yes(instance)
    got = NaeThreeSat.is_yes(out)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH")
        print("  input   :", instance)
        print("  output  :", out)
        print("  expected:", expected, " got:", got)
        raise AssertionError("reduction mismatch")


def main():
    # 1. Exhaustive over every valid 3-SAT instance with num_vars <= 3.
    for instance in ThreeSat.enumerate_instances(3):
        check(instance)

    # 2. Random small instances at scales 3..6 (brute force still feasible).
    rng = random.Random(12345)
    for scale in range(0, 7):
        for _ in range(40):
            check(ThreeSat.random_instance(rng, scale))

    # 3. A few hand-built edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 1, "clauses": []})
    check({"num_vars": 2, "clauses": []})
    # Unsatisfiable 3-SAT core.
    check({"num_vars": 3, "clauses": [
        [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
        [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3]]})
    # Trivially satisfiable.
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    # Duplicate clauses.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()


def extra():
    """Additional stress tests appended to main via this helper."""
    global tests_run, tests_passed
    rng = random.Random(999)
    for scale in range(3, 9):
        for _ in range(30):
            inst = ThreeSat.random_instance(rng, scale)
            out = reduce(inst)
            tests_run += 1
            NaeThreeSat.validate(out)
            if ThreeSat.is_yes(inst) == NaeThreeSat.is_yes(out):
                tests_passed += 1
            else:
                raise AssertionError((inst, out))
    for m in range(0, 6):
        inst = {"num_vars": m, "clauses": []}
        out = reduce(inst)
        tests_run += 1
        NaeThreeSat.validate(out)
        if NaeThreeSat.is_yes(out) is True:
            tests_passed += 1
        else:
            raise AssertionError(inst)


if __name__ == "__main__":
    main()
    extra()
    print(f"FINAL tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f)
