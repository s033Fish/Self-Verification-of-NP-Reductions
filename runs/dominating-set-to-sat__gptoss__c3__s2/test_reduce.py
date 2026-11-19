import sys
from problems import DominatingSet, Sat
from reduce import reduce

def main():
    total = 0
    passed = 0
    # Use small scale for exhaustive testing
    scale = 4
    for instance in DominatingSet.enumerate_instances(scale):
        total += 1
        # Compute reduction
        sat_instance = reduce(instance)
        # Validate both
        DominatingSet.validate(instance)
        Sat.validate(sat_instance)
        # Compare answers
        yes_src = DominatingSet.is_yes(instance)
        yes_tgt = Sat.is_yes(sat_instance)
        if yes_src == yes_tgt:
            passed += 1
        else:
            print("Mismatch!", instance, sat_instance, yes_src, yes_tgt, file=sys.stderr)
    print(f"{passed}/{total} tests passed")
    # Write verdict
    import json
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    if passed != total:
        sys.exit(1)

if __name__ == "__main__":
    main()
