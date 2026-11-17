import json
import sys
from problems import SOURCE, TARGET
from reduce import reduce

def main():
    total = 0
    passed = 0
    # enumerate all source instances up to exhaustive scale (5)
    for instance in SOURCE.enumerate_instances(scale=5):
        total += 1
        source_yes = SOURCE.is_yes(instance)
        # apply reduction
        target_instance = reduce(instance)
        # validate target instance
        try:
            TARGET.validate(target_instance)
        except Exception as e:
            print("Validation error on reduced instance", instance, "error", e)
            continue
        target_yes = TARGET.is_yes(target_instance)
        if source_yes == target_yes:
            passed += 1
        else:
            print("Mismatch! source", source_yes, "target", target_yes, "instance", instance, "reduced", target_instance)
    # write verdict
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))
    return passed == total

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
