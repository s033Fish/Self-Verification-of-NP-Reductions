import itertools
import json
import random
import sys

import problems
from reduce import reduce as reduce_instance

def test_random_instances(num_trials=200):
    rng = random.Random(0)
    for _ in range(num_trials):
        # generate small graph: n up to 6
        n = rng.randint(0, 6)
        # generate random edges
        edges = []
        for u in range(n):
            for v in range(u+1, n):
                if rng.random() < 0.5:
                    edges.append([u, v])
        # random k between -1 and n+2
        k = rng.randint(-1, n+2)
        instance = {"n": n, "edges": edges, "k": k}
        # validate
        problems.Clique.validate(instance)
        # reduction
        reduced = reduce_instance(instance)
        # validate reduced instance for IndependentSet
        problems.IndependentSet.validate(reduced)
        # compare answers
        ans_src = problems.Clique.is_yes(instance)
        ans_tgt = problems.IndependentSet.is_yes(reduced)
        if ans_src != ans_tgt:
            print("Mismatch!", instance, reduced, ans_src, ans_tgt)
            return False
    return True

def test_enumerate_small(scale=3):
    # enumerate all instances up to scale (n <= scale)
    for instance in problems.Clique.enumerate_instances(scale):
        reduced = reduce_instance(instance)
        problems.IndependentSet.validate(reduced)
        if problems.Clique.is_yes(instance) != problems.IndependentSet.is_yes(reduced):
            print("Mismatch in enumeration", instance)
            return False
    return True

if __name__ == "__main__":
    ok = True
    ok &= test_random_instances()
    ok &= test_enumerate_small()
    sys.exit(0 if ok else 1)
