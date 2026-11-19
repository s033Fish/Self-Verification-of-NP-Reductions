import json, random, itertools, os, sys
from problems import ExactCover, Sat
from reduce import reduce

def exact_cover_bruteforce(inst):
    ExactCover.validate(inst)
    u = inst["universe_size"]
    sets = inst["sets"]
    n = len(sets)
    # empty universe always yes
    if u == 0:
        return True
    universe = set(range(u))
    for mask in range(1 << n):
        chosen = []
        covered = set()
        ok = True
        for i in range(n):
            if mask & (1 << i):
                s = sets[i]
                # check disjointness
                if any(e in covered for e in s):
                    ok = False
                    break
                covered.update(s)
        if ok and covered == universe:
            return True
    return False

def sat_bruteforce(inst):
    Sat.validate(inst)
    m = inst["num_vars"]
    clauses = inst["clauses"]
    # formula with no clauses is satisfiable
    if not clauses:
        return True
    for vals in itertools.product([False, True], repeat=m):
        assign = {i+1: vals[i] for i in range(m)}
        satisfied = True
        for clause in clauses:
            # empty clause unsatisfied
            if not clause:
                satisfied = False
                break
            clause_sat = False
            for lit in clause:
                var = abs(lit)
                val = assign.get(var, False)
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False

def random_exact_cover_instance(max_u=4, max_sets=5):
    u = random.randint(0, max_u)
    sets = []
    for _ in range(random.randint(0, max_sets)):
        # generate random subset
        subset = [e for e in range(u) if random.choice([True, False])]
        sets.append(subset)
    return {"universe_size": u, "sets": sets}

tests = 200
passed = 0
for _ in range(tests):
    src = random_exact_cover_instance()
    try:
        src_yes = exact_cover_bruteforce(src)
    except Exception as e:
        print("Source validation error", e)
        sys.exit(1)
    red = reduce(src)
    try:
        tgt_yes = sat_bruteforce(red)
    except Exception as e:
        print("Target validation error", e)
        sys.exit(1)
    if src_yes == tgt_yes:
        passed += 1
    else:
        print("Mismatch!", src, src_yes, red, tgt_yes)
        break

verdict = {
    "verified": passed == tests,
    "tests_run": tests,
    "tests_passed": passed,
}
with open('verdict.json', 'w') as f:
    json.dump(verdict, f, indent=2)
print(json.dumps(verdict, indent=2))
