import json
import random
from problems import Sat, IndependentSet
from reduce import reduce


def run_tests():
    rng = random.Random(0)
    total = 0
    passed = 0
    # enumerate small SAT instances: scale up to 2 variables
    for instance in Sat.enumerate_instances(scale=2):
        total += 1
        sat_ans = Sat.is_yes(instance)
        ind_instance = reduce(instance)
        ind_ans = IndependentSet.is_yes(ind_instance)
        if sat_ans == ind_ans:
            passed += 1
        else:
            print("Mismatch!", instance, sat_ans, ind_instance, ind_ans)
            break
    # also test some random instances up to 3 vars
    for _ in range(100):
        total += 1
        inst = Sat.random_instance(rng, scale=3)
        sat_ans = Sat.is_yes(inst)
        ind_inst = reduce(inst)
        ind_ans = IndependentSet.is_yes(ind_inst)
        if sat_ans == ind_ans:
            passed += 1
        else:
            print("Random mismatch!", inst, sat_ans, ind_inst, ind_ans)
            break
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
