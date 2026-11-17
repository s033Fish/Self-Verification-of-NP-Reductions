import sys
import traceback
from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce

def run_tests(max_n=5):
    total = 0
    passed = 0
    # enumerate all instances up to max_n using enumerate_instances (scale is max_n)
    for instance in HamiltonianPath.enumerate_instances(max_n):
        total += 1
        try:
            # validate source
            HamiltonianPath.validate(instance)
            # reduce
            target = reduce(instance)
            # validate target
            HamiltonianCycle.validate(target)
            # compare answers
            src_yes = HamiltonianPath.is_yes(instance)
            tgt_yes = HamiltonianCycle.is_yes(target)
            if src_yes == tgt_yes:
                passed += 1
            else:
                print("Mismatch!", instance, target, src_yes, tgt_yes)
        except Exception as e:
            print("Error on instance", instance)
            traceback.print_exc()
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests(5)
    print(f"Tests run: {total}, passed: {passed}")
    import json
    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    sys.exit(0 if total == passed else 1)
