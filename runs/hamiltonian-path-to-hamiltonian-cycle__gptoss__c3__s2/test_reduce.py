import sys
import traceback
from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce


def run_tests():
    passed = 0
    total = 0
    # Test all small instances up to n=4 (scale 4). enumerate_instances uses scale param.
    for instance in HamiltonianPath.enumerate_instances(4):
        total += 1
        try:
            src_yes = HamiltonianPath.is_yes(instance)
            tgt_instance = reduce(instance)
            tgt_yes = HamiltonianCycle.is_yes(tgt_instance)
            if src_yes == tgt_yes:
                passed += 1
            else:
                print("FAIL mismatch", instance, src_yes, tgt_yes, tgt_instance, file=sys.stderr)
        except Exception as e:
            print("FAIL exception", instance, e, file=sys.stderr)
            traceback.print_exc()
    print(json.dumps({"verified": passed == total, "tests_run": total, "tests_passed": passed}))

if __name__ == "__main__":
    import json
    run_tests()
