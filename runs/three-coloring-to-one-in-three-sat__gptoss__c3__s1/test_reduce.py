import itertools
import json
from problems import ThreeColoring, OneInThreeSat
from reduce import reduce

def run_tests(max_n=4):
    passed = 0
    total = 0
    for instance in ThreeColoring.enumerate_instances(max_n):
        total += 1
        reduced = reduce(instance)
        # Validate reduced instance (should not raise)
        OneInThreeSat.validate(reduced)
        yes_source = ThreeColoring.is_yes(instance)
        yes_target = OneInThreeSat.is_yes(reduced)
        if yes_source == yes_target:
            passed += 1
        else:
            print("Mismatch!", instance, reduced)
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests(4)
    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
