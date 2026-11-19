import json, random
from problems import SubsetSum, Sat
from reduce import reduce

def main():
    rng = random.Random(0)
    total_cases = 0
    passed = 0
    # Enumerate small instances (scale up to 3)
    for scale in range(0, 4):
        for inst in SubsetSum.enumerate_instances(scale):
            total_cases += 1
            yes1 = SubsetSum.is_yes(inst)
            sat_inst = reduce(inst)
            Sat.validate(sat_inst)
            yes2 = Sat.is_yes(sat_inst)
            if yes1 == yes2:
                passed += 1
            else:
                print("Mismatch", inst, yes1, yes2)
                return False, total_cases, passed
    # Random tests
    for _ in range(200):
        inst = SubsetSum.random_instance(rng, 4)
        total_cases += 1
        yes1 = SubsetSum.is_yes(inst)
        sat_inst = reduce(inst)
        Sat.validate(sat_inst)
        yes2 = Sat.is_yes(sat_inst)
        if yes1 != yes2:
            print("Random mismatch", inst, yes1, yes2)
            return False, total_cases, passed
        passed += 1
    return True, total_cases, passed

if __name__ == "__main__":
    ok, total, passed = main()
    verdict = {"verified": ok, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print("VERDICT", verdict)
    exit(0 if ok else 1)
