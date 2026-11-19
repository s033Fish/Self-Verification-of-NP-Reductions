import json
from problems import ThreeColoring, ThreeSat
from reduce import reduce


def run_tests(max_scale=4):
    total = 0
    passed = 0
    for instance in ThreeColoring.enumerate_instances(max_scale):
        total += 1
        src_yes = ThreeColoring.is_yes(instance)
        # Reduce
        tgt_instance = reduce(instance)
        # Validate target format
        try:
            ThreeSat.validate(tgt_instance)
        except Exception as e:
            raise AssertionError(f"Target validation failed for {instance}: {e}")
        tgt_yes = ThreeSat.is_yes(tgt_instance)
        if src_yes == tgt_yes:
            passed += 1
        else:
            raise AssertionError(
                f"Mismatch on instance {instance}: src_yes={src_yes}, tgt_yes={tgt_yes}"
            )
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
