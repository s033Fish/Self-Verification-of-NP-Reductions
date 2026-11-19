import random
from problems import ThreeSat, VertexCover
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    ThreeSat.validate(instance)
    reduced = reduce(instance)
    VertexCover.validate(reduced)
    expected = ThreeSat.is_yes(instance)
    got = VertexCover.is_yes(reduced)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH")
        print("source:", instance)
        print("expected:", expected, "got:", got)
        print("reduced:", reduced)
    return expected == got


def main():
    # Edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 5, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]})
    check({"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 4]]})

    # Exhaustive over all formulas with num_vars <= 3 (distinct clauses).
    for instance in ThreeSat.enumerate_instances(3):
        check(instance)

    # Random instances across small scales (brute force VC is exponential).
    rng = random.Random(12345)
    for scale in range(0, 7):
        for _ in range(30):
            instance = ThreeSat.random_instance(rng, scale)
            check(instance)

    # Random instances with duplicate clauses, bounded size.
    for _ in range(300):
        m = rng.randint(3, 5)
        clauses = []
        for _ in range(rng.randint(1, 5)):
            variables = rng.sample(range(1, m + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in sorted(variables)])
        if clauses and rng.random() < 0.5:
            clauses.append(list(clauses[0]))
        check({"num_vars": m, "clauses": clauses})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"


if __name__ == "__main__":
    main()
