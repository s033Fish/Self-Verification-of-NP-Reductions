import random
import sys
import json
from problems import Sat, ThreeSat
from sat_solver import sat_satisfiable, three_sat_satisfiable
from reduce import reduce

def random_instance(max_vars=4, max_clauses=5, max_lits=5):
    num_vars = random.randint(0, max_vars)
    clauses = []
    for _ in range(random.randint(0, max_clauses)):
        k = random.randint(0, max_lits)  # may be zero literals
        clause = []
        for __ in range(k):
            if num_vars == 0:
                # no variables, can't create literals, break
                break
            var = random.randint(1, num_vars)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}

def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        inst = random_instance()
        # Validate source instance (may raise InvalidInstance)
        try:
            Sat.validate(inst)
        except Exception as e:
            print(f"Invalid source instance generated: {e}", file=sys.stderr)
            continue
        # Compute answers
        ans_sat = sat_satisfiable(inst)
        # Reduce
        red = reduce(inst)
        # Validate target instance
        try:
            ThreeSat.validate(red)
        except Exception as e:
            print(f"Reduced instance invalid on test {i}: {e}", file=sys.stderr)
            return False, passed, i+1
        ans_three = three_sat_satisfiable(red)
        if ans_sat != ans_three:
            print(f"Mismatch on test {i}: source {ans_sat}, reduced {ans_three}", file=sys.stderr)
            print("source", json.dumps(inst))
            print("reduced", json.dumps(red))
            return False, passed, i+1
        passed += 1
    return True, passed, num_tests

if __name__ == "__main__":
    ok, passed, total = run_tests()
    result = {"verified": ok, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result))
    sys.exit(0 if ok else 1)
