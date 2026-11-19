import itertools, random, json, sys
from problems import OneInThreeSat, ExactCover
from reduce import reduce

def solve_one_in_three(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in itertools.product([0,1], repeat=m):
        ok = True
        for clause in clauses:
            true_cnt = sum(bits[var-1] for var in clause)
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False

def solve_exact_cover(instance):
    u = instance['universe_size']
    sets = instance['sets']
    n = len(sets)
    # precompute bitmask for each set
    masks = []
    for s in sets:
        mask = 0
        for e in s:
            mask |= 1 << e
        masks.append(mask)
    full = (1 << u) - 1
    for r in range(1 << n):
        used = 0
        ok = True
        for i in range(n):
            if r >> i & 1:
                if used & masks[i]:
                    ok = False
                    break
                used |= masks[i]
        if ok and used == full:
            return True
    return False

def random_instance(max_vars=4, max_clauses=4):
    m = random.randint(0, max_vars)
    # ensure at least 3 if there are clauses
    if m < 3:
        maxc = 0
    else:
        maxc = max_clauses
    c = random.randint(0, maxc)
    clauses = []
    for _ in range(c):
        # pick 3 distinct vars from 1..m
        if m >= 3:
            clause = random.sample(range(1, m+1), 3)
            clauses.append(clause)
    return {'num_vars': m, 'clauses': clauses}

random.seed(0)
tests = 0
passed = 0
for _ in range(200):
    inst = random_instance()
    # validate source
    OneInThreeSat.validate(inst)
    red = reduce(inst)
    ExactCover.validate(red)
    ans_src = solve_one_in_three(inst)
    ans_tgt = solve_exact_cover(red)
    tests += 1
    if ans_src == ans_tgt:
        passed += 1
    else:
        print('Mismatch', inst, red, ans_src, ans_tgt)
        sys.exit(1)

# also test some edge cases manually
edge_cases = [
    {'num_vars': 0, 'clauses': []},
    {'num_vars': 3, 'clauses': []},
    {'num_vars': 3, 'clauses': [[1,2,3]]},
]
for inst in edge_cases:
    OneInThreeSat.validate(inst)
    red = reduce(inst)
    ExactCover.validate(red)
    ans_src = solve_one_in_three(inst)
    ans_tgt = solve_exact_cover(red)
    tests += 1
    if ans_src == ans_tgt:
        passed += 1
    else:
        print('Mismatch edge', inst, red, ans_src, ans_tgt)
        sys.exit(1)

verdict = {'verified': passed == tests, 'tests_run': tests, 'tests_passed': passed}
print(json.dumps(verdict))
with open('verdict.json', 'w') as f:
    json.dump(verdict, f)
