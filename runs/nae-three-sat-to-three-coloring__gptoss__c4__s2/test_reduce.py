import random
import itertools
import sys
from problems import NaeThreeSat, ThreeColoring
from reduce import reduce

def nae3sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            vals = []
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit < 0:
                    val = not val
                vals.append(val)
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False

def threecolor_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    colors = [-1] * n
    def backtrack(v: int) -> bool:
        if v == n:
            return True
        for c in range(3):
            conflict = False
            for nb in adj[v]:
                if colors[nb] == c:
                    conflict = True
                    break
            if conflict:
                continue
            colors[v] = c
            if backtrack(v + 1):
                return True
            colors[v] = -1
        return False
    return backtrack(0)

def random_nae_instance(max_vars=3, max_clauses=1):
    m = random.randint(0, max_vars)
    clauses = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        if m < 3:
            break
        vars = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars:
            clause.append(v if random.choice([True, False]) else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(30):  # limited tests for speed
        inst = random_nae_instance()
        NaeThreeSat.validate(inst)
        reduced = reduce(inst)
        ThreeColoring.validate(reduced)
        ans1 = nae3sat_bruteforce(inst)
        ans2 = threecolor_bruteforce(reduced)
        total += 1
        if ans1 == ans2:
            passed += 1
        else:
            print('Mismatch!')
            print('Instance:', inst)
            print('Reduced:', reduced)
            sys.exit(1)
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1,2,3]]},
        {"num_vars": 3, "clauses": [[1,2,3], [-1,-2,-3]]},
    ]
    for inst in edge_cases:
        NaeThreeSat.validate(inst)
        reduced = reduce(inst)
        ThreeColoring.validate(reduced)
        ans1 = nae3sat_bruteforce(inst)
        ans2 = threecolor_bruteforce(reduced)
        total += 1
        if ans1 == ans2:
            passed += 1
        else:
            print('Edge case mismatch', inst)
            sys.exit(1)
    print('All tests passed', passed, '/', total)
    with open('verdict.json','w') as f:
        f.write('{"verified": true, "tests_run": %d, "tests_passed": %d}' % (total, passed))

if __name__ == '__main__':
    main()
