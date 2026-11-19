import sys
import json
from problems import HamiltonianPath, Sat
from reduce import reduce

def main():
    max_scale = 4  # vertices up to 4 for exhaustive testing
    total = 0
    passed = 0
    for instance in HamiltonianPath.enumerate_instances(max_scale):
        total += 1
        hp_yes = HamiltonianPath.is_yes(instance)
        sat_instance = reduce(instance)
        # Validate target instance
        Sat.validate(sat_instance)
        sat_yes = Sat.is_yes(sat_instance)
        if hp_yes == sat_yes:
            passed += 1
        else:
            print("Mismatch!", instance, hp_yes, sat_yes, file=sys.stderr)
            break
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
