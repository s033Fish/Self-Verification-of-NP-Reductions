import json
from problems import ThreeColoring, ThreeSat
from reduce import reduce

def main():
    total = 0
    passed = 0
    # enumerate small graphs up to scale 4 (covers edge cases like K4)
    for instance in ThreeColoring.enumerate_instances(scale=4):
        total += 1
        reduced = reduce(instance)
        ans_src = ThreeColoring.is_yes(instance)
        ans_tgt = ThreeSat.is_yes(reduced)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", instance, reduced, ans_src, ans_tgt)
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
