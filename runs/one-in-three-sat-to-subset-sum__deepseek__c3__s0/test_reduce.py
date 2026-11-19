import random
import sys

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
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH", instance, "->", out, "expected", expected, "got", got)
        return False
    return True


def main():
    ok = True

    # Exhaustive: every 1-in-3-SAT formula with num_vars <= 4 (distinct clauses).
    for scale in range(0, 5):
        for instance in SOURCE.enumerate_instances(scale):
            if not check(instance):
                ok = False

    # Random larger instances, including duplicate clauses and unused vars.
    rng = random.Random(12345)
    for _ in range(400):
        m = rng.randint(0, 8)
        k = rng.randint(0, 12)
        clauses = []
        for _ in range(k):
            if m < 3:
                break
            clauses.append(sorted(rng.sample(range(1, m + 1), 3)))
        instance = {"num_vars": m, "clauses": clauses}
        if not check(instance):
            ok = False

    # Instances produced by the problem's own random generator.
    for seed in range(60):
        r = random.Random(seed)
        for scale in (3, 4, 5, 6, 7, 8):
            instance = SOURCE.random_instance(r, scale)
            if not check(instance):
                ok = False

    # Explicit edge cases.
    for instance in [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]},
    ]:
        if not check(instance):
            ok = False


    # Larger random instances (scale up to 11) to stress the encoding.
    rng2 = random.Random(999)
    for _ in range(120):
        m = rng2.randint(3, 11)
        k = rng2.randint(0, 14)
        clauses = [sorted(rng2.sample(range(1, m + 1), 3)) for _ in range(k)]
        if not check({"num_vars": m, "clauses": clauses}):
            ok = False

    # Every formula on exactly 5 variables (all subsets of the 10 clauses).
    for instance in SOURCE.enumerate_instances(5):
        if instance["num_vars"] != 5:
            continue
        if not check(instance):
            ok = False

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    import json
    with open("verdict.json", "w") as fh:
        json.dump({"verified": bool(ok), "tests_run": tests_run, "tests_passed": tests_passed}, fh)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

# appended stress additions are handled inside main via the following block
