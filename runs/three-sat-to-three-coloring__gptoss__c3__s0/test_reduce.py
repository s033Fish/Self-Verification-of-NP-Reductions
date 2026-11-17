import sys
from problems import SOURCE, TARGET
from reduce import reduce

def main():
    total = 0
    passed = 0
    # Exhaustive enumeration up to scale 3 (as defined in SOURCE)
    for instance in SOURCE.enumerate_instances(scale=3):
        total += 1
        try:
            target = reduce(instance)
            source_yes = SOURCE.is_yes(instance)
            target_yes = TARGET.is_yes(target)
            if source_yes == target_yes:
                passed += 1
            else:
                print("Mismatch!", instance, source_yes, target_yes, file=sys.stderr)
        except Exception as e:
            print("Error on instance", instance, e, file=sys.stderr)
    # Also test a few random instances
    import random
    rng = random.Random(0)
    for scale in range(0, 5):
        for _ in range(20):
            total += 1
            instance = SOURCE.random_instance(rng, scale)
            try:
                target = reduce(instance)
                source_yes = SOURCE.is_yes(instance)
                target_yes = TARGET.is_yes(target)
                if source_yes == target_yes:
                    passed += 1
                else:
                    print("Random mismatch!", instance, source_yes, target_yes, file=sys.stderr)
            except Exception as e:
                print("Random error on instance", instance, e, file=sys.stderr)
    # Write verdict.json
    import json
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
