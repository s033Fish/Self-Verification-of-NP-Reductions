import json
from problems import SOURCE, TARGET
from reduce import reduce


def run_tests(max_scale: int = 4):
    total = 0
    passed = 0
    for instance in SOURCE.enumerate_instances(max_scale):
        total += 1
        src_yes = SOURCE.is_yes(instance)
        tgt_inst = reduce(instance)
        tgt_yes = TARGET.is_yes(tgt_inst)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("Mismatch!", instance, src_yes, tgt_yes)
            break
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests(4)
    verdict = {"verified": total == passed, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(verdict)

def run_random_tests(num=100, scale=6):
    import random
    rng = random.Random(0)
    total = 0
    passed = 0
    for _ in range(num):
        inst = SOURCE.random_instance(rng, scale)
        total += 1
        src_yes = SOURCE.is_yes(inst)
        tgt_inst = reduce(inst)
        tgt_yes = TARGET.is_yes(tgt_inst)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("Random mismatch!", inst, src_yes, tgt_yes)
            break
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests(4)
    r_total, r_passed = run_random_tests(200, 6)
    total += r_total
    passed += r_passed
    verdict = {"verified": total == passed, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(verdict)
