import json
from problems import VertexCover, SetCover
from reduce import reduce


def run_tests(max_scale: int = 3):
    total = 0
    passed = 0
    for instance in VertexCover.enumerate_instances(max_scale):
        total += 1
        reduced = reduce(instance)
        # compare answers
        ans_src = VertexCover.is_yes(instance)
        ans_tgt = SetCover.is_yes(reduced)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", instance, reduced, ans_src, ans_tgt)
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests(3)
    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
