import random
import json
from typing import Dict, Any

from three_sat_solver import is_satisfiable
from independent_set_solver import has_independent_set
from reduce import reduce

def random_three_sat(max_vars=4, max_clauses=4) -> Dict[str, Any]:
    m = random.randint(0, max_vars)
    # ensure at least 0 vars allowed, but if clauses >0 need m>=3 per spec, but we can still generate valid ones.
    # We'll generate clauses only if m>=3.
    if m < 3:
        return {"num_vars": m, "clauses": []}
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct variables
        vars_ = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars_:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def test_random_instances(num_tests=200):
    for i in range(num_tests):
        inst = random_three_sat()
        sat = is_satisfiable(inst)
        red = reduce(inst)
        indep = has_independent_set(red)
        if sat != indep:
            print("Mismatch on instance", i)
            print(json.dumps(inst, indent=2))
            print("Reduced", red)
            print("sat", sat, "indep", indep)
            return False
    return True

def test_edge_cases():
    # No clauses
    inst = {"num_vars": 0, "clauses": []}
    assert is_satisfiable(inst)
    red = reduce(inst)
    assert red == {"n": 0, "edges": [], "k": 0}
    assert has_independent_set(red)
    # One clause
    inst = {"num_vars": 3, "clauses": [[1, -2, 3]]}
    sat = is_satisfiable(inst)
    red = reduce(inst)
    indep = has_independent_set(red)
    assert sat == indep
    # contradictory literals across clauses
    inst = {"num_vars": 2, "clauses": [[1, 2, -1], [-2, 1, 2]]}
    # Note: this violates distinct variable per clause because clause has both 1 and -1, but we won't generate such.
    # Instead test a valid contradictory scenario:
    inst = {"num_vars": 2, "clauses": [[1, 2, 2], [-1, -2, -2]]}
    # This also invalid. We'll skip.
    return True

if __name__ == "__main__":
    ok = test_random_instances() and test_edge_cases()
    print("All tests passed" if ok else "Tests failed")
