import random

from problems import SOURCE, TARGET
from reduce import reduce


def run_tests():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    # Exhaustive small instances via the source enumerator.
    for scale in range(0, 6):
        for inst in SOURCE.enumerate_instances(scale):
            SOURCE.validate(inst)
            out = reduce(inst)
            TARGET.validate(out)
            tests_run += 1
            src = SOURCE.is_yes(inst)
            tgt = TARGET.is_yes(out)
            if src == tgt:
                tests_passed += 1
            else:
                print("MISMATCH", inst, "->", out, src, tgt)

    # Random instances, including negative and large k values.
    for _ in range(3000):
        scale = rng.randint(0, 7)
        inst = SOURCE.random_instance(rng, scale)
        # Also probe unusual k values directly.
        if rng.random() < 0.3:
            inst = dict(inst)
            inst["k"] = rng.randint(-3, inst["n"] + 3)
        SOURCE.validate(inst)
        out = reduce(inst)
        TARGET.validate(out)
        tests_run += 1
        src = SOURCE.is_yes(inst)
        tgt = TARGET.is_yes(out)
        if src == tgt:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "->", out, src, tgt)

    return tests_run, tests_passed


if __name__ == "__main__":
    run, passed = run_tests()
    print(f"tests_run={run} tests_passed={passed}")
    assert run == passed, "some tests failed"
