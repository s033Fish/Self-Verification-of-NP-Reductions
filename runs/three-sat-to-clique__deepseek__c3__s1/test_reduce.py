import random
from itertools import combinations, product

from problems import ThreeSat, Clique
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(inst):
    global tests_run, tests_passed
    tests_run += 1
    ThreeSat.validate(inst)
    out = reduce(inst)
    Clique.validate(out)
    a = ThreeSat.is_yes(inst)
    b = Clique.is_yes(out)
    if a != b:
        raise AssertionError(f"MISMATCH src={inst} -> {out}: {a} vs {b}")
    tests_passed += 1


# 1. Exhaustive small formulas over num_vars 0..3, distinct clauses.
for num_vars in range(0, 4):
    all_clauses = [
        [s * v for s, v in zip(signs, variables)]
        for variables in combinations(range(1, num_vars + 1), 3)
        for signs in product((1, -1), repeat=3)
    ]
    for mask in range(1 << len(all_clauses)):
        clauses = [c for i, c in enumerate(all_clauses) if mask >> i & 1]
        check({"num_vars": num_vars, "clauses": clauses})

# 2. Hand-picked edge cases.
check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
check({"num_vars": 5, "clauses": [[1, 2, 3], [-1, -2, -3]]})
check({"num_vars": 4, "clauses": [[1, 2, 3], [-1, 2, 4], [1, -2, 4], [1, 2, -4]]})
check({"num_vars": 0, "clauses": []})
check({"num_vars": 7, "clauses": []})
check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3],
                                   [-1, -2, 3], [-1, 2, -3], [1, -2, -3], [-1, -2, -3]]})

# 3. Random instances via the problem generator.
rng = random.Random(12345)
counts = {0: 40, 1: 40, 2: 40, 3: 40, 4: 40, 5: 30, 6: 8}
for scale, count in counts.items():
    for _ in range(count):
        check(ThreeSat.random_instance(rng, scale))

# 4. Random instances with extra duplicated clauses.
for _ in range(200):
    scale = rng.randint(3, 5)
    inst = ThreeSat.random_instance(rng, scale)
    if inst["clauses"]:
        inst["clauses"].append(list(rng.choice(inst["clauses"])))
    check(inst)

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
