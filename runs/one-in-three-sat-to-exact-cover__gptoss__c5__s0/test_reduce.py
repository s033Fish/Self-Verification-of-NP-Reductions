import itertools
import sys
from typing import List, Dict

from problems import OneInThreeSat, ExactCover
from solve_bruteforce import solve_one_in_three_sat, solve_exact_cover
from reduce import reduce as reduce_instance


def generate_instances(max_vars: int = 4, max_clauses: int = 3) -> List[Dict]:
    instances = []
    for num_vars in range(0, max_vars + 1):
        # generate all possible clauses (as sorted tuples) for this num_vars
        var_range = list(range(1, num_vars + 1))
        possible_clauses = []
        if len(var_range) >= 3:
            for combo in itertools.combinations(var_range, 3):
                possible_clauses.append(list(combo))
        # also allow empty clause list
        for num_clauses in range(0, max_clauses + 1):
            if num_clauses == 0:
                instances.append({"num_vars": num_vars, "clauses": []})
                continue
            if not possible_clauses:
                # cannot have clauses if not enough vars, skip
                continue
            # generate all sequences of clauses (allow repetitions)
            for clause_seq in itertools.product(possible_clauses, repeat=num_clauses):
                # deep copy each clause list
                clauses = [list(c) for c in clause_seq]
                instances.append({"num_vars": num_vars, "clauses": clauses})
    return instances


def main():
    instances = generate_instances()
    total = len(instances)
    passed = 0
    for idx, inst in enumerate(instances, 1):
        try:
            src_ans = solve_one_in_three_sat(inst)
        except Exception as e:
            print(f"Validation error on source instance {inst}: {e}")
            sys.exit(1)
        reduced = reduce_instance(inst)
        try:
            tgt_ans = solve_exact_cover(reduced)
        except Exception as e:
            print(f"Validation error on reduced instance {reduced}: {e}")
            sys.exit(1)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", idx, "source", inst, "src_ans", src_ans, "tgt_ans", tgt_ans)
    # write verdict.json
    import json
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
