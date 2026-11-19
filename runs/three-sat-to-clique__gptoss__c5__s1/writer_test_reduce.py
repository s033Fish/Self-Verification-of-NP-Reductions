import itertools
import random
from typing import List, Dict, Any

from problems import ThreeSat, Clique
from solve_three_sat import solve as solve_three_sat
from solve_clique import solve as solve_clique
from reduce import reduce as reduce_instance


def generate_all_instances(max_vars: int, max_clauses: int) -> List[Dict[str, Any]]:
    instances = []
    # include empty formula case
    instances.append({"num_vars": 0, "clauses": []})
    for m in range(1, max_vars + 1):
        vars_range = list(range(1, m + 1))
        # generate possible clauses (choose 3 distinct vars)
        if m < 3:
            continue
        possible_clauses = []
        for vars_combo in itertools.combinations(vars_range, 3):
            for signs in itertools.product([1, -1], repeat=3):
                clause = [sign * var for sign, var in zip(signs, vars_combo)]
                possible_clauses.append(clause)
        # generate formulas with up to max_clauses clauses (allow repetitions)
        for num_clauses in range(1, max_clauses + 1):
            for clause_tuple in itertools.product(possible_clauses, repeat=num_clauses):
                instances.append({"num_vars": m, "clauses": [list(c) for c in clause_tuple]})
    return instances


def test_random_small_instances():
    # generate a limited set to keep test time reasonable
    instances = generate_all_instances(max_vars=3, max_clauses=2)
    random.shuffle(instances)
    # test first 200 instances
    for inst in instances[:200]:
        ThreeSat.validate(inst)
        reduced = reduce_instance(inst)
        Clique.validate(reduced)
        ans_src = solve_three_sat(inst)
        ans_tgt = solve_clique(reduced)
        assert ans_src == ans_tgt, f"Mismatch on {inst} -> {reduced}: {ans_src} vs {ans_tgt}"

if __name__ == "__main__":
    test_random_small_instances()
    print("All tests passed")
