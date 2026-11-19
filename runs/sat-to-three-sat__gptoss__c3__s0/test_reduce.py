import sys
from problems import Sat, ThreeSat
from reduce import reduce

def main():
    max_scale = 2  # keep enumeration small for speed
    total = 0
    passed = 0
    for inst in Sat.enumerate_instances(max_scale):
        total += 1
        try:
            yes_sat = Sat.is_yes(inst)
            red = reduce(inst)
            yes_three = ThreeSat.is_yes(red)
            if yes_sat == yes_three:
                passed += 1
            else:
                print("Mismatch!", inst, yes_sat, yes_three)
        except Exception as e:
            print("Error on instance", inst, e)
            sys.exit(1)
    print(f"Tests run: {total}, passed: {passed}")
    # Write verdict.json
    import json
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    if not verdict["verified"]:
        sys.exit(1)

if __name__ == "__main__":
    main()
