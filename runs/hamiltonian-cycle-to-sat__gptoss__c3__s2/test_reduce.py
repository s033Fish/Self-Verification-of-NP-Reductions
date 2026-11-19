import sys
import traceback
from problems import HamiltonianCycle, Sat
from reduce import reduce

def run_tests():
    total = 0
    passed = 0
    # Enumerate small graphs up to scale 4 (n <= 4). The enumerate_instances
    # yields all graphs with n up to the given scale.
    for instance in HamiltonianCycle.enumerate_instances(scale=4):
        total += 1
        try:
            src = HamiltonianCycle.is_yes(instance)
            tgt_inst = reduce(instance)
            tgt = Sat.is_yes(tgt_inst)
            if src != tgt:
                print("Mismatch!", instance, src, tgt)
                continue
            passed += 1
        except Exception as e:
            print("Error on instance", instance)
            traceback.print_exc()
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    verified = total == passed
    # Write verdict.json
    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": verified, "tests_run": total, "tests_passed": passed}, f)
    print(json.dumps({"verified": verified, "tests_run": total, "tests_passed": passed}))
