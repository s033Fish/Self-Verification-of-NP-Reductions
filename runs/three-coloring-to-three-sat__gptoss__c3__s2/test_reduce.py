import json
from problems import ThreeColoring, ThreeSat
from reduce import reduce


def main():
    total = 0
    passed = 0
    # Enumerate all graphs with up to 4 vertices (scale 4)
    for instance in ThreeColoring.enumerate_instances(scale=4):
        total += 1
        try:
            sat_inst = reduce(instance)
            source_yes = ThreeColoring.is_yes(instance)
            target_yes = ThreeSat.is_yes(sat_inst)
            if source_yes == target_yes:
                passed += 1
            else:
                print("Mismatch!", instance, source_yes, target_yes)
        except Exception as e:
            print("Error on instance", instance, e)
    # Write verdict
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
