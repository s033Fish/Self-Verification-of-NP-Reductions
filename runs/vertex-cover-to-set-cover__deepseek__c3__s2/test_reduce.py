import random
import problems
from reduce import reduce

SOURCE = problems.VertexCover
TARGET = problems.SetCover


def run_tests():
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        SOURCE.validate(instance)
        reduced = reduce(instance)
        TARGET.validate(reduced)
        expected = SOURCE.is_yes(instance)
        got = TARGET.is_yes(reduced)
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH", instance, "->", reduced, "expected", expected, "got", got)

    # Enumerate all small vertex-cover instances.
    for scale in range(0, 5):
        for instance in SOURCE.enumerate_instances(scale):
            check(instance)

    # Random instances across several scales.
    rng = random.Random(12345)
    for scale in range(0, 9):
        for _ in range(300):
            check(SOURCE.random_instance(rng, scale))

    # Explicit edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": -1})
    check({"n": 3, "edges": [], "k": 0})
    check({"n": 3, "edges": [], "k": -1})
    check({"n": 3, "edges": [[0, 1], [1, 2]], "k": 1})
    check({"n": 3, "edges": [[0, 1], [1, 2]], "k": 2})
    check({"n": 3, "edges": [[0, 1], [1, 2]], "k": 0})
    check({"n": 3, "edges": [[0, 1], [1, 2]], "k": -5})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 1})
    check({"n": 5, "edges": [[0, 1]], "k": 1})

    return tests_run, tests_passed


if __name__ == "__main__":
    run, passed = run_tests()
    print(f"tests_run={run} tests_passed={passed}")
    assert run == passed, "some tests failed"
