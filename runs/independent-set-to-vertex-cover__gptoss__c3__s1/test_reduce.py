import random
import sys

import problems
from reduce import reduce

def main():
    rng = random.Random(0)
    total = 0
    passed = 0
    # Test a variety of small random instances
    for scale in range(1, 5):  # small scales
        for _ in range(200):
            total += 1
            src = problems.SOURCE.random_instance(rng, scale)
            # Ensure instance is valid (should be by generator)
            try:
                problems.SOURCE.validate(src)
            except Exception as e:
                print("Invalid source instance generated", e)
                sys.exit(1)
            tgt = reduce(src)
            # Validate target
            try:
                problems.TARGET.validate(tgt)
            except Exception as e:
                print("Reduced instance invalid", e)
                sys.exit(1)
            src_yes = problems.SOURCE.is_yes(src)
            tgt_yes = problems.TARGET.is_yes(tgt)
            if src_yes == tgt_yes:
                passed += 1
            else:
                print("Mismatch!", src, tgt, src_yes, tgt_yes)
                sys.exit(1)
    # Also exhaustively enumerate very tiny graphs
    for src in problems.SOURCE.enumerate_instances(2):
        total += 1
        tgt = reduce(src)
        if problems.SOURCE.is_yes(src) != problems.TARGET.is_yes(tgt):
            print("Mismatch in enumeration", src)
            sys.exit(1)
        passed += 1
    print(f"tests_run: {total}, tests_passed: {passed}")
    # Write verdict.json
    import json
    verdict = {"verified": True, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == "__main__":
    main()
