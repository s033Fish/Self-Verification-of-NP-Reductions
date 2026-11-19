import itertools
import random
import json
import sys

import problems
from reduce import reduce

def test_all_small(scale=3, max_instances=2000):
    count = 0
    for instance in problems.Clique.enumerate_instances(scale):
        # limit number
        if count >= max_instances:
            break
        # reduce
        sat_inst = reduce(instance)
        # validate both
        problems.Clique.validate(instance)
        problems.Sat.validate(sat_inst)
        # compare answers
        ans_clique = problems.Clique.is_yes(instance)
        ans_sat = problems.Sat.is_yes(sat_inst)
        if ans_clique != ans_sat:
            print("Mismatch!", instance, sat_inst, ans_clique, ans_sat)
            return False
        count += 1
    print(f"All {count} instances matched.")
    return True

def test_edge_cases():
    # k <= 0
    inst = {"n": 5, "edges": [], "k": 0}
    assert problems.Clique.is_yes(inst)
    sat = reduce(inst)
    assert problems.Sat.is_yes(sat)
    # k == 1, n >=1
    inst = {"n": 3, "edges": [], "k": 1}
    assert problems.Clique.is_yes(inst)
    sat = reduce(inst)
    assert problems.Sat.is_yes(sat)
    # k > n
    inst = {"n": 2, "edges": [], "k": 3}
    assert not problems.Clique.is_yes(inst)
    sat = reduce(inst)
    assert not problems.Sat.is_yes(sat)

if __name__ == "__main__":
    ok = test_all_small()
    test_edge_cases()
    sys.exit(0 if ok else 1)
