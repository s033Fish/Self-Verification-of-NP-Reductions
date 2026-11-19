import json
from problems import VertexCover, IndependentSet
from reduce import reduce


def run_tests(max_scale=4):
    total = 0
    passed = 0
    for scale in range(max_scale + 1):
        for instance in VertexCover.enumerate_instances(scale):
            total += 1
            src_yes = VertexCover.is_yes(instance)
            tgt_instance = reduce(instance)
            tgt_yes = IndependentSet.is_yes(tgt_instance)
            if src_yes == tgt_yes:
                passed += 1
            else:
                print("Mismatch!", instance, src_yes, tgt_yes)
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    print(f"Tests run: {total}, passed: {passed}")
    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))
