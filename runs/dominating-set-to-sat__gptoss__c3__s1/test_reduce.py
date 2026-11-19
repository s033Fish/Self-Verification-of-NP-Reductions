import json
from problems import DominatingSet, Sat
from reduce import reduce

def main():
    scale = 3  # small enough for exhaustive enumeration
    total = 0
    passed = 0
    for instance in DominatingSet.enumerate_instances(scale):
        total += 1
        sat_instance = reduce(instance)
        # validate both (will raise if invalid)
        DominatingSet.validate(instance)
        Sat.validate(sat_instance)
        expected = DominatingSet.is_yes(instance)
        got = Sat.is_yes(sat_instance)
        if expected == got:
            passed += 1
        else:
            print("Mismatch!", instance, sat_instance, expected, got)
            break
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
