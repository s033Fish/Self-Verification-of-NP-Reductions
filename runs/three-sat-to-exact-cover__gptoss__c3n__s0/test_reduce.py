import itertools, random, json
from problems import ThreeSat, ExactCover
from reduce import reduce

def solve_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            satisfied = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0 and val:
                    satisfied = True
                if lit < 0 and not val:
                    satisfied = True
                if satisfied:
                    break
            if not satisfied:
                ok = False
                break
        if ok:
            return True
    return False

def solve_exact_cover(instance):
    u = instance['universe_size']
    sets = instance['sets']
    n = len(sets)
    # brute force over subsets
    for mask in range(1 << n):
        covered = [0] * u
        ok = True
        for i in range(n):
            if (mask >> i) & 1:
                for e in sets[i]:
                    covered[e] += 1
                    if covered[e] > 1:
                        ok = False
                        break
                if not ok:
                    break
        if ok and all(c == 1 for c in covered):
            return True
    return False

def random_three_sat(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    if m < 3:
        max_c = 0
    else:
        max_c = max_clauses
    n = random.randint(0, max_c)
    clauses = []
    for _ in range(n):
        # pick 3 distinct vars from 1..m
        vars = random.sample(range(1, m+1), 3) if m >= 3 else []
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
        inst = random_three_sat()
        # validate
        ThreeSat.validate(inst)
        red = reduce(inst)
        ExactCover.validate(red)
        ans1 = solve_three_sat(inst)
        ans2 = solve_exact_cover(red)
        if ans1 == ans2:
            passed += 1
        else:
            print('Mismatch!')
            print('3SAT:', json.dumps(inst))
            print('ExactCover:', json.dumps(red))
            print('answers', ans1, ans2)
            break
    print(f'Passed {passed}/{tests}')
    # write verdict
    verdict = {"verified": passed == tests, "tests_run": tests, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
