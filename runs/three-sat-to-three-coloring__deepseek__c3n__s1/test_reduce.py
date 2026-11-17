import json
import random

from problems import ThreeSat, ThreeColoring
from reduce import reduce
from solvers import sat_solve, coloring_solve

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    ThreeSat.validate(instance)
    target = reduce(instance)
    ThreeColoring.validate(target)
    expected = sat_solve(instance)
    got = coloring_solve(target)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH", instance, "expected", expected, "got", got)
        print("target", target)


def rand_instance(rng, max_vars=5, max_clauses=6):
    m = rng.randint(0, max_vars)
    clauses = []
    if m >= 3:
        for _ in range(rng.randint(0, max_clauses)):
            vs = rng.sample(range(1, m + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    return {"num_vars": m, "clauses": clauses}


def main():
    # Explicit edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 1, "clauses": []})
    check({"num_vars": 3, "clauses": []})
    # All 8 clauses over 3 vars -> unsatisfiable.
    import itertools
    all_clauses = []
    for signs in itertools.product([1, -1], repeat=3):
        all_clauses.append([signs[i] * (i + 1) for i in range(3)])
    check({"num_vars": 3, "clauses": all_clauses})
    # Duplicate clauses.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    # Unused variables.
    check({"num_vars": 5, "clauses": [[1, 2, 3]]})
    check({"num_vars": 5, "clauses": [[-1, -2, -3]]})

    rng = random.Random(12345)
    for _ in range(3000):
        check(rand_instance(rng))

    verdict = {"verified": tests_run == tests_passed, "tests_run": tests_run,
               "tests_passed": tests_passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))


if __name__ == "__main__":
    main()
