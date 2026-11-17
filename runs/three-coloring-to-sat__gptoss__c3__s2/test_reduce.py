import sys
from problems import ThreeColoring, Sat
from reduce import reduce

def main():
    total = 0
    passed = 0
    # Enumerate all graphs up to n=4 (scale parameter controls max n)
    for instance in ThreeColoring.enumerate_instances(4):
        total += 1
        # Reduce and compare answers
        sat_instance = reduce(instance)
        ans_src = ThreeColoring.is_yes(instance)
        ans_tgt = Sat.is_yes(sat_instance)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", instance, sat_instance, ans_src, ans_tgt, file=sys.stderr)
            break
    # Write verdict file
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    import json
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
