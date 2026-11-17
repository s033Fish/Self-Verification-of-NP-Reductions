import json
from problems import ThreeSat, ThreeColoring
from reduce import reduce


def main():
    scale = 3  # small enough to enumerate all instances
    total = 0
    passed = 0
    for instance in ThreeSat.enumerate_instances(scale):
        total += 1
        # Validate source (should already be valid)
        ThreeSat.validate(instance)
        source_yes = ThreeSat.is_yes(instance)
        target_instance = reduce(instance)
        # Validate target format
        ThreeColoring.validate(target_instance)
        target_yes = ThreeColoring.is_yes(target_instance)
        if source_yes == target_yes:
            passed += 1
        else:
            print("Mismatch!", instance, source_yes, target_yes)
            break
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)


if __name__ == "__main__":
    main()
