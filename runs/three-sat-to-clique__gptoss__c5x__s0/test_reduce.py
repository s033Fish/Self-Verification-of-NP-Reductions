"""Independent tests for reduce.py (3-SAT -> Clique)."""
import itertools
import random

from problems import ThreeSat, Clique
from solvers import sat_solve, clique_solve
from reduce import reduce

TESTS_RUN = 0
TESTS_PASSED = 0


def check(inst):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    # source must be valid
    ThreeSat.validate(inst)
    src = sat_solve(inst)
    out = reduce(inst)
    # target must be valid
    Clique.validate(out)
    tgt = clique_solve(out)
    assert src == tgt, f"MISMATCH src={src} tgt={tgt} inst={inst} out={out}"
    TESTS_PASSED += 1


def all_clauses(m):
    """All valid clauses over variables 1..m (choose 3 distinct vars, signs)."""
    clauses = []
    for vars_ in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            clauses.append([s * v for s, v in zip(signs, vars_)])
    return clauses


def main():
    global TESTS_RUN, TESTS_PASSED
    random.seed(12345)

    # 1. Empty formula for many m, including m = 0.
    for m in range(0, 8):
        check({"num_vars": m, "clauses": []})

    # 2. Exhaustive-ish: all single clauses for m up to 5.
    for m in range(3, 6):
        for cl in all_clauses(m):
            check({"num_vars": m, "clauses": [cl]})

    # 3. Exhaustive pairs/triples of clauses for small m.
    for m in (3, 4):
        cls = all_clauses(m)
        for _ in range(1500):
            k = random.randint(1, 4)
            chosen = [random.choice(cls) for _ in range(k)]
            check({"num_vars": m, "clauses": chosen})

    # 4. Random formulas with varying m and clause counts, including
    #    duplicates and unused variables.
    for _ in range(1500):
        m = random.randint(3, 6)
        cls = all_clauses(m)
        k = random.randint(1, 4)
        chosen = [list(random.choice(cls)) for _ in range(k)]
        # sometimes duplicate a clause
        if random.random() < 0.3 and chosen:
            chosen.append(list(random.choice(chosen)))
        # sometimes shuffle literal order
        for c in chosen:
            random.shuffle(c)
        check({"num_vars": m, "clauses": chosen})

    # 5. Larger m with no clauses / unused variables.
    for m in (10, 50, 200):
        check({"num_vars": m, "clauses": []})
        cl = [1, 2, 3]
        check({"num_vars": m, "clauses": [cl]})

    # 6. Unsatisfiable instances (all 8 clauses over 3 vars) and variants.
    unsat = all_clauses(3)
    check({"num_vars": 3, "clauses": unsat})
    check({"num_vars": 3, "clauses": unsat + unsat})
    check({"num_vars": 4, "clauses": unsat})

    # 7. Sanity: reduction output structure for a known case.
    out = reduce({"num_vars": 3, "clauses": [[1, 2, 3]]})
    assert out["n"] == 3 and out["k"] == 1
    assert out["edges"] == []  # no edges within a single clause
    TESTS_RUN += 1
    TESTS_PASSED += 1

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED


if __name__ == "__main__":
    main()
