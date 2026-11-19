import random
import json
from problems import OneInThreeSat, ExactCover
from reduce import reduce


def run_tests(num_trials: int = 200) -> dict:
    rng = random.Random(0)
    passed = 0
    total = 0
    # include edge cases manually
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1,2,3]]},
    ]
    for inst in edge_cases:
        total += 1
        src = OneInThreeSat.is_yes(inst)
        tgt = ExactCover.is_yes(reduce(inst))
        if src == tgt:
            passed += 1
    # random instances
    for _ in range(num_trials):
        scale = rng.randint(0, 4)  # small number of variables
        inst = OneInThreeSat.random_instance(rng, scale)
        total += 1
        src = OneInThreeSat.is_yes(inst)
        tgt = ExactCover.is_yes(reduce(inst))
        if src == tgt:
            passed += 1
        else:
            print("Mismatch!", inst, src, tgt)
            break
    return {"tests_run": total, "tests_passed": passed}

if __name__ == "__main__":
    result = run_tests(500)
    result["verified"] = result["tests_run"] == result["tests_passed"]
    print(json.dumps(result, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
