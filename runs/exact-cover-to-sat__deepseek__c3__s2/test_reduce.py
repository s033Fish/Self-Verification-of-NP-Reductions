import random
from itertools import combinations, product

from problems import ExactCover, Sat
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    ExactCover.validate(instance)
    out = reduce(instance)
    Sat.validate(out)
    expected = ExactCover.is_yes(instance)
    got = Sat.is_yes(out)
    assert expected == got, (instance, out, expected, got)
    tests_passed += 1


def all_subsets(elements):
    for r in range(len(elements) + 1):
        for c in combinations(elements, r):
            yield list(c)


def exhaustive_small():
    # All set systems over universes 0..3 with up to 3 sets drawn from all
    # subsets (including empty), allowing duplicates.
    for u in range(0, 4):
        universe = list(range(u))
        subsets = list(all_subsets(universe))
        for count in range(0, 4):
            for combo in product(subsets, repeat=count):
                check({"universe_size": u, "sets": [list(s) for s in combo]})


def random_tests(n):
    rng = random.Random(12345)
    for _ in range(n):
        u = rng.randint(0, 6)
        num_sets = rng.randint(0, 8)
        sets = []
        for _ in range(num_sets):
            k = rng.randint(0, u)
            sets.append(sorted(rng.sample(range(u), k)))
        check({"universe_size": u, "sets": sets})


def planted_tests(n):
    rng = random.Random(999)
    for _ in range(n):
        u = rng.randint(0, 7)
        sets = []
        if u > 0 and rng.random() < 0.6:
            elems = list(range(u))
            rng.shuffle(elems)
            cuts = sorted(rng.sample(range(1, u), rng.randint(0, u - 1))) if u > 1 else []
            for start, end in zip([0, *cuts], [*cuts, u]):
                sets.append(sorted(elems[start:end]))
        for _ in range(rng.randint(0, 8)):
            k = rng.randint(0, u)
            sets.append(sorted(rng.sample(range(u), k)))
        rng.shuffle(sets)
        check({"universe_size": u, "sets": sets})


def duplicate_tests():
    check({"universe_size": 2, "sets": [[0, 1], [0, 1]]})          # no
    check({"universe_size": 2, "sets": [[0], [1], [0], [1]]})      # yes
    check({"universe_size": 0, "sets": [[], [], []]})              # yes
    check({"universe_size": 1, "sets": [[], [0], [0]]})            # yes
    check({"universe_size": 2, "sets": [[0], [0], [1]]})           # yes
    check({"universe_size": 3, "sets": [[0, 1], [1, 2], [2, 0]]})  # no


def random_instance_tests(n):
    rng = random.Random(2024)
    for _ in range(n):
        scale = rng.randint(0, 8)
        inst = ExactCover.random_instance(rng, scale)
        check(inst)


if __name__ == "__main__":
    exhaustive_small()
    random_tests(400)
    planted_tests(400)
    duplicate_tests()
    random_instance_tests(500)
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
