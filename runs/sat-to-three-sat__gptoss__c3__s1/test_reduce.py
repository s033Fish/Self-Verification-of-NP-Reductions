import sys
from problems import Sat, ThreeSat
from reduce import reduce

def main():
    total = 0
    passed = 0
    # Enumerate all SAT instances with up to 2 variables (scale=2) to keep runtime modest
    for instance in Sat.enumerate_instances(2):
        total += 1
        # Validate source (should be valid)
        Sat.validate(instance)
        reduced = reduce(instance)
        # Validate target
        ThreeSat.validate(reduced)
        yes_src = Sat.is_yes(instance)
        yes_tgt = ThreeSat.is_yes(reduced)
        if yes_src == yes_tgt:
            passed += 1
        else:
            print("Mismatch!", instance, reduced, yes_src, yes_tgt)
    print(f"TOTAL {total} PASSED {passed}")
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    import json, pathlib
    pathlib.Path('verdict.json').write_text(json.dumps(verdict))

if __name__ == "__main__":
    main()
