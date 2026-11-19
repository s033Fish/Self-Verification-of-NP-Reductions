import sys
import json
import traceback
from typing import Tuple

import problems
from reduce import reduce


def run_test(instance) -> Tuple[bool, str]:
    try:
        # Validate source instance (should be valid)
        problems.IndependentSet.validate(instance)
        source_yes = problems.IndependentSet.is_yes(instance)
        # Reduce
        target_instance = reduce(instance)
        # Validate target instance as Clique
        problems.Clique.validate(target_instance)
        target_yes = problems.Clique.is_yes(target_instance)
        if source_yes != target_yes:
            return False, f"Mismatch: source {source_yes}, target {target_yes}, instance {instance}, reduced {target_instance}"
        return True, ""
    except Exception as e:
        return False, f"Exception {e!r}: {traceback.format_exc()}"


def main():
    scale = 4  # small enough for exhaustive enumeration
    total = 0
    passed = 0
    for instance in problems.IndependentSet.enumerate_instances(scale):
        total += 1
        ok, msg = run_test(instance)
        if ok:
            passed += 1
        else:
            print("FAIL", msg, file=sys.stderr)
    # Write verdict
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict, indent=2))
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
