import itertools, random, json, sys
from problems import ThreeSat, DominatingSet
from reduce import reduce

def solve_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # iterate over assignments as bits 0..(1<<m)-1
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (mask >> var) & 1  # 1 means true
                if (lit > 0 and val == 1) or (lit < 0 and val == 0):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def solve_dominating_set(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k < 0:
        return False
    # adjacency list including self
    adj = [set([i]) for i in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # try all subsets up to k (if k >= n, always yes)
    if k >= n:
        return True
    for size in range(k + 1):
        for combo in itertools.combinations(range(n), size):
            dominated = set()
            for v in combo:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False

# generate random small 3-SAT instances respecting constraints
def random_three_sat(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if any clause
    possible_vars = list(range(1, m + 1))
    clauses = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        if m < 3:
            # cannot create clause, break
            break
        # pick 3 distinct vars
        vars3 = random.sample(possible_vars, 3)
        clause = []
        for v in vars3:
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
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        DominatingSet.validate(reduced)
        ans_src = solve_three_sat(inst)
        ans_tgt = solve_dominating_set(reduced)
        total += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch!')
            print('src', inst, ans_src)
            print('tgt', reduced, ans_tgt)
            sys.exit(1)
    print('All tests passed', passed, '/', total)
    # write verdict
    verdict = {"verified": True, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
