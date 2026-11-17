import json
from problems import ThreeSat, ThreeColoring
from reduce import reduce


def main():
    total = 0
    passed = 0
    # enumerate all instances with num_vars <= 3 (scale=3)
    for instance in ThreeSat.enumerate_instances(scale=3):
        total += 1
        try:
            target = reduce(instance)
        except Exception as e:
            print("Reduction raised exception on", instance, e)
            continue
        src_yes = ThreeSat.is_yes(instance)
        tgt_yes = ThreeColoring.is_yes(target)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("Mismatch!", instance, src_yes, tgt_yes)
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
