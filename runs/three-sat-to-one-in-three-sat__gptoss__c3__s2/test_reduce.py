import random
import json
from problems import ThreeSat, OneInThreeSat
from reduce import reduce


def run_tests():
    tests_run = 0
    tests_passed = 0
    # Edge case: empty formula
    empty = {"num_vars": 0, "clauses": []}
    try:
        ThreeSat.validate(empty)
    except Exception as e:
        print("Validation failed for empty source", e)
        return 0,0
    target = reduce(empty)
    OneInThreeSat.validate(target)
    if ThreeSat.is_yes(empty) == OneInThreeSat.is_yes(target):
        tests_passed += 1
    tests_run += 1

    # Random small instances
    rng = random.Random(0)
    for scale in range(1,5):  # scales up to 4
        for _ in range(30):
            src = ThreeSat.random_instance(rng, scale)
            # ensure validation passes
            ThreeSat.validate(src)
            tgt = reduce(src)
            OneInThreeSat.validate(tgt)
            src_yes = ThreeSat.is_yes(src)
            tgt_yes = OneInThreeSat.is_yes(tgt)
            if src_yes == tgt_yes:
                tests_passed += 1
            else:
                print("Mismatch!", src, src_yes, tgt, tgt_yes)
            tests_run += 1
    return tests_run, tests_passed

if __name__ == "__main__":
    run, passed = run_tests()
    verdict = {"verified": run==passed, "tests_run": run, "tests_passed": passed}
    print(json.dumps(verdict))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
