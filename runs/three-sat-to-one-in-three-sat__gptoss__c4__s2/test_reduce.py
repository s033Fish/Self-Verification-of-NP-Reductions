import itertools, random, sys
from typing import List, Dict, Any

# import reduce function
from reduce import reduce as reduction

def three_sat_solve(instance: Dict[str, Any]) -> bool:
    m = instance['num_vars']
    clauses = instance['clauses']
    for assign in itertools.product([0,1], repeat=m):
        ok = True
        for clause in clauses:
            satisfied = False
            for lit in clause:
                v = abs(lit)-1
                val = assign[v]
                if (lit > 0 and val==1) or (lit < 0 and val==0):
                    satisfied = True
                    break
            if not satisfied:
                ok=False
                break
        if ok:
            return True
    return False

def one_in_three_sat_solve(instance: Dict[str, Any]) -> bool:
    m = instance['num_vars']
    clauses = instance['clauses']
    for assign in itertools.product([0,1], repeat=m):
        ok = True
        for clause in clauses:
            cnt = sum(assign[v-1] for v in clause)
            if cnt != 1:
                ok=False
                break
        if ok:
            return True
    return False

def random_three_sat(m, num_clauses):
    """Generate a random 3‑SAT instance respecting the problem constraints.
+
+    For m < 3 we cannot create a clause with three distinct variables, so we
+    simply return an instance with no clauses (which is trivially satisfiable).
+    """
    clauses = []
    vars = list(range(1, m + 1))
    if m >= 3:
        for _ in range(num_clauses):
            trio = random.sample(vars, 3)
            clause = []
            for v in trio:
                lit = v if random.choice([True, False]) else -v
                clause.append(lit)
            clauses.append(clause)
    return {'num_vars': m, 'clauses': clauses}

random.seed(0)

tests = 0
passed = 0
for m in range(0,5):
    for num_clauses in range(0,5):
        for _ in range(30):
            inst = random_three_sat(m, num_clauses)
            three_res = three_sat_solve(inst)
            reduced = reduction(inst)
            one_res = one_in_three_sat_solve(reduced)
            tests += 1
            if three_res == one_res:
                passed += 1
            else:
                print('FAIL', inst, three_res, one_res)
                sys.exit(1)
print('All tests passed', passed, '/', tests)
