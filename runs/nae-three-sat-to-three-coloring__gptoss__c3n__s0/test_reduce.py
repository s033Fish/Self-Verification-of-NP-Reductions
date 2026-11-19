import random
import json
from typing import List, Dict

from nae_three_sat_solver import is_satisfiable
from three_color_solver import is_three_colorable
from reduce import reduce

def random_instance(max_vars=3, max_clauses=1) -> Dict:
    m = random.randint(0, max_vars)
    clauses: List[List[int]] = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        if m < 3:
            break
        vars_choice = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars_choice:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def run_tests(num_tests=30):
    passed = 0
    for i in range(num_tests):
        inst = random_instance()
        sat = is_satisfiable(inst)
        graph = reduce(inst)
        color = is_three_colorable(graph)
        if sat == color:
            passed += 1
        else:
            print("Mismatch on instance", i)
            print(json.dumps(inst, indent=2))
            print("NAE result", sat)
            print("Graph", graph)
            print("Color result", color)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests()
    print(f"Passed {passed}/{total} tests")
