import random
import sys

from problems import SOURCE, TARGET
from reduce import reduce


def run_tests(num_random=200):
    rng = random.Random(0)
    passed = 0
    total = 0
    # Edge case tests
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
    ]
    for inst in edge_cases:
        total += 1
        try:
            SOURCE.validate(inst)
            vc = reduce(inst)
            TARGET.validate(vc)
            if SOURCE.is_yes(inst) == TARGET.is_yes(vc):
                passed += 1
            else:
                print("Mismatch on edge case", inst, "->", vc, file=sys.stderr)
        except Exception as e:
            print("Error on edge case", inst, e, file=sys.stderr)

    # Random tests
    for scale in range(0, 4):  # variables up to 3
        for _ in range(num_random):
            inst = SOURCE.random_instance(rng, scale)
            total += 1
            try:
                SOURCE.validate(inst)
                vc = reduce(inst)
                TARGET.validate(vc)
                if SOURCE.is_yes(inst) == TARGET.is_yes(vc):
                    passed += 1
                else:
                    print("Mismatch", inst, vc, file=sys.stderr)
            except Exception as e:
                print("Error", e, file=sys.stderr)
    return passed, total

if __name__ == "__main__":
    passed, total = run_tests()
    print(f"Passed {passed}/{total} tests")
    # Write verdict.json
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    import json, pathlib
    pathlib.Path("verdict.json").write_text(json.dumps(verdict))
    if passed != total:
        sys.exit(1)
