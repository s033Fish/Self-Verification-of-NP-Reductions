import json
from problems import ExactCover, Sat
from reduce import reduce


def run_tests(max_scale: int = 3):
    total = 0
    passed = 0
    for instance in ExactCover.enumerate_instances(max_scale):
        total += 1
        yes_ec = ExactCover.is_yes(instance)
        sat_inst = reduce(instance)
        # Validate SAT instance (optional)
        Sat.validate(sat_inst)
        yes_sat = Sat.is_yes(sat_inst)
        if yes_ec != yes_sat:
            print("Mismatch!", instance, yes_ec, yes_sat)
            raise AssertionError("Reduction failed on instance")
        passed += 1
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests(3)
    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
