import json
from problems import SubsetSum, Partition
from reduce import reduce


def run_tests():
    total = 0
    passed = 0
    # Enumerate small instances (scale up to 4)
    for instance in SubsetSum.enumerate_instances(4):
        total += 1
        try:
            src_ans = SubsetSum.is_yes(instance)
            tgt_instance = reduce(instance)
            tgt_ans = Partition.is_yes(tgt_instance)
            if src_ans == tgt_ans:
                passed += 1
            else:
                print("Mismatch", instance, tgt_instance, src_ans, tgt_ans)
        except Exception as e:
            print("Error on instance", instance, e)
    # Also test some random instances
    rng = __import__('random').Random(0)
    for _ in range(200):
        instance = SubsetSum.random_instance(rng, scale=5)
        total += 1
        src_ans = SubsetSum.is_yes(instance)
        tgt_instance = reduce(instance)
        tgt_ans = Partition.is_yes(tgt_instance)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Random mismatch", instance, tgt_instance, src_ans, tgt_ans)
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
