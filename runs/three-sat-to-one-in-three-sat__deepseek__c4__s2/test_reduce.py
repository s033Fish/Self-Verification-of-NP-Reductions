"""Tests comparing brute-force answers on 3-SAT instances and their reductions."""
import itertools
import random
from reduce import reduce
from solvers import solve_3sat, solve_1in3
import problems


def random_instance(rng, max_m=8, max_c=12):
    m = rng.randint(0, max_m)
    ncl = rng.randint(0, max_c)
    if ncl and m < 3:
        m = 3
    clauses = []
    for _ in range(ncl):
        vs = rng.sample(range(1, m + 1), 3)
        clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    if clauses and rng.random() < 0.3:
        clauses.append(list(rng.choice(clauses)))
    return {"num_vars": m, "clauses": clauses}


def all_clauses(m):
    res = []
    for vs in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            res.append([v * s for v, s in zip(vs, signs)])
    return res


def main():
    run = passed = 0
    rng = random.Random(12345)

    # fixed edge cases
    fixed = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [-1, 2, 4], [-2, -3, -4]]},
        {"num_vars": 3, "clauses": [[1, 2, 3]] * 3},
    ]

    # exhaustive small instances
    exhaustive = []
    for m in (3, 4):
        cl = all_clauses(m)
        exhaustive += [[c] for c in cl]
        exhaustive += [list(p) for p in itertools.combinations(cl, 2)]
        if m == 3:
            exhaustive += [list(p) for p in itertools.combinations(cl, 3)]
    # rebuild exhaustive with correct num_vars
    exhaustive = []
    for m in (3, 4):
        cl = all_clauses(m)
        groups = [[c] for c in cl] + [list(p) for p in itertools.combinations(cl, 2)]
        if m == 3:
            groups += [list(p) for p in itertools.combinations(cl, 3)]
        for g in groups:
            exhaustive.append({"num_vars": m, "clauses": [list(x) for x in g]})

    randoms = [random_instance(rng) for _ in range(400)]
    randoms += [random_instance(rng, 8, 12) for _ in range(200)]

    for inst in fixed + exhaustive + randoms:
        problems.ThreeSat.validate(inst)
        red = reduce(inst)
        problems.OneInThreeSat.validate(red)
        a = solve_3sat(inst)
        b = solve_1in3(red)
        run += 1
        if a == b:
            passed += 1
        else:
            print("MISMATCH", inst, "->", red, "src", a, "tgt", b)

    print(f"tests_run={run} tests_passed={passed}")
    return run, passed


if __name__ == "__main__":
    main()
