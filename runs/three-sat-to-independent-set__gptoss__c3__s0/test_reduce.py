import json
from problems import ThreeSat, IndependentSet
from reduce import reduce

def main():
    total = 0
    passed = 0
    # enumerate all 3SAT instances with up to 3 variables (scale=3)
    for instance in ThreeSat.enumerate_instances(scale=3):
        total += 1
        # reduce
        ind = reduce(instance)
        # validate target instance (will raise if invalid)
        IndependentSet.validate(ind)
        # compare answers
        src_yes = ThreeSat.is_yes(instance)
        tgt_yes = IndependentSet.is_yes(ind)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("Mismatch!", instance, ind, src_yes, tgt_yes)
    # also test some random instances
    import random
    rng = random.Random(0)
    for _ in range(100):
        instance = ThreeSat.random_instance(rng, scale=4)
        total += 1
        ind = reduce(instance)
        IndependentSet.validate(ind)
        src_yes = ThreeSat.is_yes(instance)
        tgt_yes = IndependentSet.is_yes(ind)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("Random mismatch!", instance, src_yes, tgt_yes)
    # write verdict
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
