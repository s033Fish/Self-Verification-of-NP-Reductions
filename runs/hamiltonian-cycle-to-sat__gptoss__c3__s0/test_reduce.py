import sys
from problems import HamiltonianCycle, Sat
from reduce import reduce

def main():
    max_scale = 4  # small enough for exhaustive enumeration
    total = 0
    passed = 0
    for instance in HamiltonianCycle.enumerate_instances(max_scale):
        total += 1
        src_yes = HamiltonianCycle.is_yes(instance)
        sat_instance = reduce(instance)
        sat_yes = Sat.is_yes(sat_instance)
        if src_yes == sat_yes:
            passed += 1
        else:
            print("Mismatch!", instance, src_yes, sat_yes, file=sys.stderr)
            # break on first failure
            break
    print(f"{passed}/{total} tests passed")
    # write verdict
    import json
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    if passed != total:
        sys.exit(1)

if __name__ == "__main__":
    main()
