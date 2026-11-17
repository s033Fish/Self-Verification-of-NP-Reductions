import json
import sys
from problems import ThreeSat, ExactCover
from reduce import reduce


def run_tests():
    rng = __import__('random').Random(0)
    total = 0
    passed = 0
    # test a variety of scales up to 3 (the exhaustive scale)
    for scale in range(0, 4):
        # generate 20 random instances per scale
        for _ in range(20):
            instance = ThreeSat.random_instance(rng, scale)
            total += 1
            try:
                sat_yes = ThreeSat.is_yes(instance)
                ec_instance = reduce(instance)
                ExactCover.validate(ec_instance)
                ec_yes = ExactCover.is_yes(ec_instance)
                if sat_yes == ec_yes:
                    passed += 1
                else:
                    print("Mismatch!", instance, sat_yes, ec_yes, file=sys.stderr)
            except Exception as e:
                print("Error on instance", instance, e, file=sys.stderr)
                # treat as failure
    # also test explicit edge cases
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 3, "clauses": []},
    ]
    for instance in edge_cases:
        total += 1
        try:
            sat_yes = ThreeSat.is_yes(instance)
            ec_instance = reduce(instance)
            ExactCover.validate(ec_instance)
            ec_yes = ExactCover.is_yes(ec_instance)
            if sat_yes == ec_yes:
                passed += 1
            else:
                print("Mismatch edge", instance, sat_yes, ec_yes, file=sys.stderr)
        except Exception as e:
            print("Error edge", instance, e, file=sys.stderr)
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    verified = (total == passed)
    verdict = {"verified": verified, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict))
    # exit code 0 if verified, else 1
    sys.exit(0 if verified else 1)
