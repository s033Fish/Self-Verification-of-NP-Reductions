import json
from problems import ThreeSat, DominatingSet
from reduce import reduce


def run_tests():
    total = 0
    passed = 0
    # Enumerate all ThreeSat instances with scale up to 3 (as enumeration is feasible)
    for instance in ThreeSat.enumerate_instances(scale=3):
        total += 1
        src_yes = ThreeSat.is_yes(instance)
        tgt_instance = reduce(instance)
        tgt_yes = DominatingSet.is_yes(tgt_instance)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("Mismatch!", instance, src_yes, tgt_yes)
    # Additional random tests for a few larger scales (but still small for brute force)
    import random
    rng = random.Random(0)
    for scale in range(4, 7):  # 4 to 6 variables, random instances
        for _ in range(20):
            total += 1
            inst = ThreeSat.random_instance(rng, scale)
            src_yes = ThreeSat.is_yes(inst)
            tgt_inst = reduce(inst)
            tgt_yes = DominatingSet.is_yes(tgt_inst)
            if src_yes == tgt_yes:
                passed += 1
            else:
                print("Random mismatch!", inst, src_yes, tgt_yes)
    # Write verdict
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print("Tests run:", total, "passed:", passed)
    print("Verdict written to verdict.json")

if __name__ == "__main__":
    run_tests()
