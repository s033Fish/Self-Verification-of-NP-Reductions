import itertools, random, json, sys
from problems import ThreeSat, DominatingSet
from reduce import reduce

def solve_three_sat(inst):
    m = inst['num_vars']
    clauses = inst['clauses']
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1
                if lit > 0 and val == 1:
                    sat = True
                if lit < 0 and val == 0:
                    sat = True
            if not sat:
                ok = False
                break
        if ok:
            return True
    return False

def solve_dominating_set(inst):
    n = inst['n']
    edges = inst['edges']
    k = inst['k']
    if k < 0:
        return False
    # adjacency list including self
    adj = [set([i]) for i in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # iterate subsets up to k
    for r in range(0, min(k, n) + 1):
        for combo in itertools.combinations(range(n), r):
            covered = set()
            for v in combo:
                covered.update(adj[v])
            if len(covered) == n:
                return True
    return False


def random_three_sat(max_vars=5, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure if clauses >0 then m>=3 per spec, but we can allow smaller for testing.
    c = random.randint(0, max_clauses)
    clauses = []
    for _ in range(c):
        # pick 3 distinct vars (if possible)
        if m == 0:
            break
        vars_ = random.sample(range(1, m+1), min(3, m))
        # if less than 3 distinct vars, repeat to fill length 3? For simplicity skip clause.
        if len(vars_) < 3:
            continue
        clause = []
        for v in vars_:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        inst = random_three_sat()
        # validate source
        ThreeSat.validate(inst)
        red = reduce(inst)
        DominatingSet.validate(red)
        ans_src = solve_three_sat(inst)
        ans_tgt = solve_dominating_set(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch!')
            print('src', inst)
            print('red', red)
            print('src ans', ans_src, 'tgt ans', ans_tgt)
            sys.exit(1)
        total += 1
    verdict = {"verified": True, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('All tests passed')

if __name__ == '__main__':
    main()
