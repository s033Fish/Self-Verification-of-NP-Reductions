import random
import itertools
from problems import ThreeSat, ExactCover
from reduce import reduce
from solvers import solve_three_sat, solve_exact_cover

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    ThreeSat.validate(instance)
    red = reduce(instance)
    ExactCover.validate(red)
    a = solve_three_sat(instance)
    b = solve_exact_cover(red)
    assert a == b, f"MISMATCH src={instance} src_ans={a} red={red} red_ans={b}"
    tests_passed += 1


def random_instance(m, n, rng):
    clauses = []
    for _ in range(n):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    rng = random.Random(12345)

    # edge cases: no clauses, m = 0
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 1, "clauses": []})
    check({"num_vars": 5, "clauses": []})

    # exhaustive-ish small random tests
    for m in range(3, 8):
        for n in range(0, 8):
            for _ in range(40):
                check(random_instance(m, n, rng))

    # include duplicate clauses and unused variables
    for _ in range(200):
        m = rng.randint(3, 7)
        n = rng.randint(1, 6)
        inst = random_instance(m, n, rng)
        if n >= 1:
            inst["clauses"].append(list(inst["clauses"][0]))
        check(inst)

    # exhaustive over all 3-clauses for small m
    for m in (3, 4):
        all_clauses = []
        for vs in itertools.combinations(range(1, m + 1), 3):
            for signs in itertools.product((1, -1), repeat=3):
                all_clauses.append([s * v for s, v in zip(signs, vs)])
        for _ in range(300):
            n = rng.randint(0, 5)
            clauses = [list(rng.choice(all_clauses)) for _ in range(n)]
            check({"num_vars": m, "clauses": clauses})

    # known satisfiable / unsatisfiable
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3], [-1, 2, -3]]})
    # all 8 clauses over 3 vars is unsat
    all8 = []
    for signs in itertools.product((1, -1), repeat=3):
        all8.append([s * v for s, v in zip(signs, (1, 2, 3))])
    check({"num_vars": 3, "clauses": all8})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
