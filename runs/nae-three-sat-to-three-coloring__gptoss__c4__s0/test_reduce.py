import random
import itertools
import json
from problems import NaeThreeSat, ThreeColoring
from reduce import reduce

def solve_nae(instance):
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

def solve_3color(instance):
    n = instance['n']
    edges = [(u, v) for u, v in instance['edges']]
    for colors in itertools.product([0,1,2], repeat=n):
        good = True
        for u, v in edges:
            if colors[u] == colors[v]:
                good = False
                break
        if good:
            return True
    return False

def random_nae_instance(max_vars=3, max_clauses=1):
    m = random.randint(0, max_vars)
    vars_list = list(range(1, m+1))
    clauses = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        if m < 3:
            break
        triple = random.sample(vars_list, 3)
        clause = []
        for v in triple:
            clause.append(random.choice([v, -v]))
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        inst = random_nae_instance()
        NaeThreeSat.validate(inst)
        red = reduce(inst)
        ThreeColoring.validate(red)
        ans_src = solve_nae(inst)
        ans_tgt = solve_3color(red)
        total += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch!')
            print('src', inst)
            print('red', red)
            print('src ans', ans_src, 'tgt ans', ans_tgt)
            break
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('Verdict', verdict)

if __name__ == '__main__':
    main()
