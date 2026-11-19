import random
import itertools
from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    red = reduce(instance)
    TARGET.validate(red)  # must be a valid SAT instance
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(red)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH", instance, "expected", expected, "got", got)
        print("reduction:", red)


def main():
    # 1) Exhaustive small instances (values 0..3, length <= 4) and many targets.
    for length in range(5):
        for numbers in itertools.product(range(4), repeat=length):
            numbers = list(numbers)
            total = sum(numbers)
            targets = list(range(-2, total + 3))
            targets += [total + 5, 2 ** (total.bit_length() + 2),
                        2 ** (total.bit_length() + 2) + 1, -1]
            for t in dict.fromkeys(targets):
                check({"numbers": numbers, "target": t})

    # 2) The official enumerator for small scales.
    for scale in range(5):
        for inst in SOURCE.enumerate_instances(scale):
            check(inst)

    # 3) Random instances from the problem's generator.
    rng = random.Random(12345)
    for scale in range(0, 9):
        for _ in range(200):
            check(SOURCE.random_instance(rng, scale))

    # 4) Some larger-value random instances (still brute-forceable).
    rng = random.Random(999)
    for _ in range(300):
        n = rng.randint(0, 8)
        numbers = [rng.randint(0, 20) for _ in range(n)]
        total = sum(numbers)
        t = rng.randint(-2, total + 2)
        check({"numbers": numbers, "target": t})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
