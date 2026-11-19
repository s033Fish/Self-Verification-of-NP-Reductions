"""Compare brute-force 3-SAT and Clique solvers on many small instances."""
import random
import itertools

from problems import ThreeSat, Clique
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    ThreeSat.validate(instance)
    out = reduce(instance)
    Clique.validate(out)
    expected = ThreeSat.is_yes(instance)
    got = Clique.is_yes(out)
    if expected != got:
        raise AssertionError(
            f"MISMATCH source={instance} reduced={out} "
            f"expected={expected} got={got}"
        )
    tests_passed += 1


def all_clauses_for(num_vars):
    return [
        [sign * v for sign, v in zip(signs, variables)]
        for variables in itertools.combinations(range(1, num_vars + 1), 3)
        for signs in itertools.product((1, -1), repeat=3)
    ]


def main():
    # 1. Exhaustive over all subsets of clauses for num_vars <= 3 (8 clauses).
    for num_vars in range(0, 4):
        allc = all_clauses_for(num_vars)
        for mask in range(1 << len(allc)):
            clauses = [list(c) for i, c in enumerate(allc) if mask >> i & 1]
            check({"num_vars": num_vars, "clauses": clauses})
    print("section 1 done", tests_run, flush=True)

    # 2. Random subsets for num_vars = 4,5 (32 and 256 possible clauses).
    rng = random.Random(999)
    for num_vars in (4, 5):
        allc = all_clauses_for(num_vars)
        for _ in range(300):
            r = rng.randint(0, min(len(allc), 7))
            clauses = [list(c) for c in rng.sample(allc, r)]
            check({"num_vars": num_vars, "clauses": clauses})
    print("section 2 done", tests_run, flush=True)

    # 3. Duplicate clauses.
    for num_vars in range(3, 6):
        base = [[1, 2, 3], [-1, -2, -3], [1, -2, 3]]
        base = [c for c in base if all(abs(l) <= num_vars for l in c)]
        for reps in range(1, 4):
            clauses = []
            for c in base:
                clauses.extend([list(c)] * reps)
            check({"num_vars": num_vars, "clauses": clauses})
    print("section 3 done", tests_run, flush=True)

    # 4. Random instances across small scales (keep graphs small enough to solve).
    for scale in range(0, 7):
        for _ in range(40):
            check(ThreeSat.random_instance(rng, scale))
    print("section 4 done", tests_run, flush=True)

    # 5. Edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 5, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
    check({"num_vars": 3, "clauses": all_clauses_for(3)})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
