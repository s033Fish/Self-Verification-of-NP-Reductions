import json, random
from problems import Sat, Clique
from reduce import reduce


def run_tests(num_trials: int = 200, max_scale: int = 3) -> dict:
    """Run a number of random tests.

    The original enumeration approach is infeasible for even modest scales
    because the number of distinct formulas grows exponentially.  Instead we
    sample a modest number of random instances using the provided generator
    ``Sat.random_instance`` which respects the problem's format.
    """

    rng = random.Random(0)
    total = 0
    passed = 0
    for _ in range(num_trials):
        instance = Sat.random_instance(rng, max_scale)
        total += 1
        sat_yes = Sat.is_yes(instance)
        clique_instance = reduce(instance)
        clique_yes = Clique.is_yes(clique_instance)
        if sat_yes == clique_yes:
            passed += 1
        else:
            print("Mismatch!", instance, "=>", clique_instance, sat_yes, clique_yes)
            break
    return {"total": total, "passed": passed}

if __name__ == "__main__":
    result = run_tests()
    verified = result["total"] == result["passed"]
    verdict = {"verified": verified, "tests_run": result["total"], "tests_passed": result["passed"]}
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
