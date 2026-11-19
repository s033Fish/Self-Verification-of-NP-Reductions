import json
import sys
from pathlib import Path

import problems
from reduce import reduce

def main():
    source = problems.SOURCE
    target = problems.TARGET
    total = 0
    passed = 0
    # enumerate small instances up to scale 3 (variables up to 3)
    for instance in source.enumerate_instances(scale=3):
        total += 1
        # Reduce
        try:
            reduced = reduce(instance)
        except Exception as e:
            print(f"Reduction raised on instance {instance}: {e}", file=sys.stderr)
            continue
        # Validate reduced instance
        try:
            target.validate(reduced)
        except Exception as e:
            print(f"Reduced instance invalid for {instance}: {e}", file=sys.stderr)
            continue
        src_yes = source.is_yes(instance)
        tgt_yes = target.is_yes(reduced)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("Mismatch!", instance, src_yes, tgt_yes, file=sys.stderr)
    # Write verdict
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(verdict))
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
