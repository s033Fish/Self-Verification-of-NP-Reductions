import json
from problems import NaeThreeSat, ThreeColoring
from reduce import reduce

def main():
    tests_run = 0
    tests_passed = 0
    # Enumerate small instances (scale up to 3 variables)
    for instance in NaeThreeSat.enumerate_instances(scale=3):
        tests_run += 1
        src_yes = NaeThreeSat.is_yes(instance)
        tgt_instance = reduce(instance)
        # Validate target instance (will raise if invalid)
        ThreeColoring.validate(tgt_instance)
        tgt_yes = ThreeColoring.is_yes(tgt_instance)
        if src_yes == tgt_yes:
            tests_passed += 1
        else:
            print("Mismatch!", instance, tgt_instance, src_yes, tgt_yes)
    # Also test a few random instances
    import random
    rng = random.Random(0)
    for _ in range(20):
        instance = NaeThreeSat.random_instance(rng, scale=4)
        tests_run += 1
        src_yes = NaeThreeSat.is_yes(instance)
        tgt_instance = reduce(instance)
        ThreeColoring.validate(tgt_instance)
        tgt_yes = ThreeColoring.is_yes(tgt_instance)
        if src_yes == tgt_yes:
            tests_passed += 1
        else:
            print("Random mismatch!", instance, src_yes, tgt_yes)
    verified = tests_passed == tests_run
    verdict = {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
