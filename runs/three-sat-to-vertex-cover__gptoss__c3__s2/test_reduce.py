import sys
import json
from problems import ThreeSat, VertexCover
from reduce import reduce

def main():
    passed = 0
    total = 0
    # test small formulas up to 3 variables
    for instance in ThreeSat.enumerate_instances(scale=3):
        total += 1
        yes_sat = ThreeSat.is_yes(instance)
        vc_instance = reduce(instance)
        yes_vc = VertexCover.is_yes(vc_instance)
        if yes_sat == yes_vc:
            passed += 1
        else:
            print("Mismatch!", instance, yes_sat, yes_vc, file=sys.stderr)
            # break on first failure
            break
    # also test a few random instances
    import random
    rng = random.Random(0)
    for _ in range(50):
        instance = ThreeSat.random_instance(rng, scale=4)
        total += 1
        yes_sat = ThreeSat.is_yes(instance)
        vc_instance = reduce(instance)
        yes_vc = VertexCover.is_yes(vc_instance)
        if yes_sat == yes_vc:
            passed += 1
        else:
            print("Random mismatch!", instance, yes_sat, yes_vc, file=sys.stderr)
            break
    print(passed, total)
    # write verdict
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    if passed != total:
        sys.exit(1)

if __name__ == "__main__":
    main()
