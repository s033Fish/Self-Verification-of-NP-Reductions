import json
import sys
from problems import SOURCE, TARGET
from reduce import reduce


def main():
    # We'll test all instances up to scale 4 (n up to 4). The enumerate_instances
    # yields every graph with n <= scale.
    max_scale = 4
    total = 0
    passed = 0
    for instance in SOURCE.enumerate_instances(max_scale):
        total += 1
        src_yes = SOURCE.is_yes(instance)
        tgt_instance = reduce(instance)
        tgt_yes = TARGET.is_yes(tgt_instance)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("Mismatch!", instance, src_yes, tgt_yes, file=sys.stderr)
            break
    # Write verdict
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
