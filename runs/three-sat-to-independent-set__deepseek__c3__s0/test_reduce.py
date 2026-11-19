import random

from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    target = reduce(instance)
    TARGET.validate(target)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(target)
    if expected != got:
        raise AssertionError(
            f"mismatch: source={instance!r} expected={expected} got={got} "
            f"target={target!r}"
        )
    tests_passed += 1


def main():
    # Exhaustive: every distinct-clause formula with m <= 3.
    for instance in SOURCE.enumerate_instances(3):
        check(instance)

    # Explicit edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 1, "clauses": []})
    check({"num_vars": 7, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3]]})

    # Random formulas, kept small so the exact independent-set solver in
    # problems.py stays fast (it is exponential in the graph size).
    rng = random.Random(12345)
    for scale in range(0, 6):
        for _ in range(20):
            clauses = []
            for _ in range(rng.randint(0, 3 * scale)):
                variables = rng.sample(range(1, scale + 1), 3) if scale >= 3 else []
                if not variables:
                    break
                clauses.append(
                    [v if rng.random() < 0.5 else -v for v in sorted(variables)]
                )
            check({"num_vars": scale, "clauses": clauses})

    # Denser small formulas to exercise unsatisfiable cases.
    for _ in range(120):
        scale = rng.randint(3, 5)
        clauses = []
        for _ in range(rng.randint(2 * scale, 6 * scale)):
            variables = rng.sample(range(1, scale + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in sorted(variables)])
        check({"num_vars": scale, "clauses": clauses})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")


if __name__ == "__main__":
    main()
