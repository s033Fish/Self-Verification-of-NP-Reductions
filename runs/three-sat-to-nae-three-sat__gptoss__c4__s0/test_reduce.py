import random, itertools, json
from reduce import reduce

def solve_3sat(num_vars, clauses):
    for assign in itertools.product([False, True], repeat=num_vars):
        ok = True
        for cl in clauses:
            vals = [(assign[abs(l)-1] ^ (l < 0)) for l in cl]
            if not any(vals):
                ok = False
                break
        if ok:
            return True
    return False

def solve_nae3sat(num_vars, clauses):
    for assign in itertools.product([False, True], repeat=num_vars):
        ok = True
        for cl in clauses:
            vals = [(assign[abs(l)-1] ^ (l < 0)) for l in cl]
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False

def random_instance(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses per spec
    if m < 3:
        # may still generate zero clauses
        pass
    clauses = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        if m < 3:
            # cannot form a valid clause, skip creating any
            continue
        vars = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def main():
    tests = 200
    passed = 0
    for _ in range(tests):
        inst = random_instance()
        red = reduce(inst)
        # ensure target format valid
        src_yes = solve_3sat(inst["num_vars"], inst["clauses"])
        tgt_yes = solve_nae3sat(red["num_vars"], red["clauses"])
        if src_yes == tgt_yes:
            passed += 1
        else:
            print('FAIL')
            print('src', inst)
            print('src_yes', src_yes)
            print('red', red)
            print('tgt_yes', tgt_yes)
            break
    print('tests run', tests, 'passed', passed)
    with open('verdict.json','w') as f:
        json.dump({"verified": passed==tests, "tests_run": tests, "tests_passed": passed}, f)

if __name__ == '__main__':
    main()
