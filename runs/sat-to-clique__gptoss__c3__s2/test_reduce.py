import json
import random
import sys
from problems import Sat, Clique
from reduce import reduce

def run_tests():
    total = 0
    passed = 0
    # Exhaustive small instances (scale up to 2)
    for inst in Sat.enumerate_instances(scale=2):
        total += 1
        sat_yes = Sat.is_yes(inst)
        clique_inst = reduce(inst)
        Clique.validate(clique_inst)
        clique_yes = Clique.is_yes(clique_inst)
        if sat_yes == clique_yes:
            passed += 1
        else:
            print("Mismatch!", inst, sat_yes, clique_yes, file=sys.stderr)
    # Random tests
    rng = random.Random(0)
    for _ in range(100):
        scale = rng.randint(0, 4)
        inst = Sat.random_instance(rng, scale)
        total += 1
        sat_yes = Sat.is_yes(inst)
        clique_inst = reduce(inst)
        Clique.validate(clique_inst)
        clique_yes = Clique.is_yes(clique_inst)
        if sat_yes == clique_yes:
            passed += 1
        else:
            print("Random mismatch!", inst, sat_yes, clique_yes, file=sys.stderr)
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    verified = (total == passed)
    verdict = {"verified": verified, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
