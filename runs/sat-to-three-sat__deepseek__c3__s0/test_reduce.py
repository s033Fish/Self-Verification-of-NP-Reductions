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
    out = reduce(instance)
    TARGET.validate(out)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(out)
    assert got == expected, (
        f"MISMATCH: source={instance} expected={expected} got={got} out={out}"
    )
    tests_passed += 1


# --- Hand-picked edge cases -------------------------------------------------
hand = [
    {"num_vars": 0, "clauses": []},
    {"num_vars": 0, "clauses": [[]]},
    {"num_vars": 1, "clauses": []},
    {"num_vars": 1, "clauses": [[1]]},
    {"num_vars": 1, "clauses": [[-1]]},
    {"num_vars": 1, "clauses": [[1], [-1]]},
    {"num_vars": 1, "clauses": [[1, -1]]},
    {"num_vars": 2, "clauses": [[1, 2]]},
    {"num_vars": 2, "clauses": [[1, 2], [-1], [-2]]},
    {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
    {"num_vars": 4, "clauses": [[1, 2, 3, 4]]},
    {"num_vars": 5, "clauses": [[1, 2, 3, 4, 5]]},
    {"num_vars": 5, "clauses": [[1, 2, 3, 4, 5], [-1, -2, -3, -4, -5]]},
    {"num_vars": 6, "clauses": [[1, 2, 3, 4, 5, 6]]},
    {"num_vars": 4, "clauses": [[1, 1, 1, 1], [2, 2, 2]]},
    {"num_vars": 4, "clauses": [[1, -1, 2, 3], [-2, -3, 4]]},
    {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
    {"num_vars": 3, "clauses": [[1, 2, 3, -1, -2, -3]]},
    {"num_vars": 2, "clauses": [[1], [2], [-1], [-2]]},
    {"num_vars": 8, "clauses": [[1, -2, 3, -4, 5, -6, 7, -8]]},
    {"num_vars": 8, "clauses": [[1, 2, 3, 4, 5, 6, 7, 8], [-1], [-2], [-3], [-4], [-5], [-6], [-7], [-8]]},
]
for inst in hand:
    check(inst)

# --- Exhaustive small instances (m <= 2) -----------------------------------
for m in range(0, 3):
    all_clauses = [
        [s * v for s, v in zip(signs, range(1, m + 1)) if s]
        for signs in itertools.product((0, 1, -1), repeat=m)
    ]
    for mask in range(1 << len(all_clauses)):
        inst = {
            "num_vars": m,
            "clauses": [c for i, c in enumerate(all_clauses) if mask >> i & 1],
        }
        check(inst)

# --- Random instances -------------------------------------------------------
rng = random.Random(12345)
for _ in range(2000):
    scale = rng.randint(0, 6)
    inst = SOURCE.random_instance(rng, scale)
    check(inst)

# --- Random instances with heavy duplication / tautologies ------------------
for _ in range(2000):
    m = rng.randint(0, 5)
    nclauses = rng.randint(0, 6)
    clauses = []
    for _ in range(nclauses):
        k = rng.randint(0, 5)
        clause = []
        for _ in range(k):
            if m == 0:
                break
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    check({"num_vars": m, "clauses": clauses})

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
