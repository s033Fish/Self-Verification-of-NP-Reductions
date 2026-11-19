import itertools
import json
import sys
from typing import List, Dict

from reduce import reduce as reduce_fn
from three_sat_solver import solve_three_sat
from independent_set_solver import solve_independent_set

def generate_instances(max_vars: int = 3, max_clauses: int = 2) -> List[Dict]:
    instances = []
    for num_vars in range(0, max_vars + 1):
        # generate all possible clauses for this num_vars
        clauses_pool: List[List[int]] = []
        if num_vars >= 3:
            for vars_triplet in itertools.combinations(range(1, num_vars + 1), 3):
                for signs in itertools.product([1, -1], repeat=3):
                    clause = [signs[i] * vars_triplet[i] for i in range(3)]
                    clauses_pool.append(clause)
        # also allow empty clause list
        for num_clauses in range(0, max_clauses + 1):
            if num_clauses == 0:
                instances.append({"num_vars": num_vars, "clauses": []})
                continue
            # generate all possible lists of clauses (allow repetitions) using product
            for clause_list in itertools.product(clauses_pool, repeat=num_clauses):
                instances.append({"num_vars": num_vars, "clauses": [list(c) for c in clause_list]})
    return instances


def main():
    instances = generate_instances()
    total = len(instances)
    passed = 0
    for idx, inst in enumerate(instances, 1):
        try:
            sat_ans = solve_three_sat(inst)
            reduced = reduce_fn(inst)
            indep_ans = solve_independent_set(reduced)
            if sat_ans == indep_ans:
                passed += 1
            else:
                print(f"Mismatch on instance {idx}/{total}: {inst}")
                print(f"  sat={sat_ans}, indep={indep_ans}, reduced={reduced}")
        except Exception as e:
            print(f"Error on instance {idx}/{total}: {e}")
            raise
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
