import json
import sys
from problems import Clique, IndependentSet
from reduce import reduce

def run_tests(max_scale=4):
    total = 0
    passed = 0
    for instance in Clique.enumerate_instances(max_scale):
        total += 1
        src_yes = Clique.is_yes(instance)
        tgt_instance = reduce(instance)
        tgt_yes = IndependentSet.is_yes(tgt_instance)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("Mismatch!", instance, src_yes, tgt_yes, file=sys.stderr)
            break
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
