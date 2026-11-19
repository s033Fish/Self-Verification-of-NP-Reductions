import random
from typing import List, Dict, Any

from problems import ThreeSat, Clique
from solve_three_sat import is_satisfiable
from solve_clique import has_clique
from reduce import reduce

def random_three_sat_instance(max_vars: int = 4, max_clauses: int = 4) -> Dict[str, Any]:
    """Generate a random but valid 3‑SAT instance respecting the problem constraints."""
    m = random.randint(0, max_vars)
    # If we have less than 3 variables, we cannot have any clauses.
    if m < 3:
        num_clauses = 0
    else:
        num_clauses = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        vars = random.sample(range(1, m + 1), 3)
        clause: List[int] = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def test_random_instances(num_tests: int = 200) -> bool:
    for _ in range(num_tests):
        inst = random_three_sat_instance()
        # Validate instance
        ThreeSat.validate(inst)
        sat = is_satisfiable(inst)
        clique_inst = reduce(inst)
        Clique.validate(clique_inst)
        has = has_clique(clique_inst)
        if sat != has:
            print("Mismatch!", inst, "sat", sat, "clique", has, "reduced", clique_inst)
            return False
    return True

if __name__ == "__main__":
    ok = test_random_instances(500)
    print("All tests passed" if ok else "Some tests failed")
