import random
import sys

import problems
from reduce import reduce


def test_random(num_trials=200):
    rng = random.Random(0)
    for _ in range(num_trials):
        # random scale 0-4 variables
        m = rng.randint(0, 4)
        # generate random 3SAT instance via provided generator
        instance = problems.ThreeSat.random_instance(rng, m)
        # ensure validation passes
        problems.ThreeSat.validate(instance)
        # reduce
        sub = reduce(instance)
        problems.SubsetSum.validate(sub)
        # compare answers
        ans_sat = problems.ThreeSat.is_yes(instance)
        ans_sum = problems.SubsetSum.is_yes(sub)
        if ans_sat != ans_sum:
            print("Mismatch!", instance, sub, ans_sat, ans_sum)
            return False
    return True


def test_edge_cases():
    # No clauses, various m
    for m in range(0, 5):
        inst = {"num_vars": m, "clauses": []}
        problems.ThreeSat.validate(inst)
        sub = reduce(inst)
        problems.SubsetSum.validate(sub)
        assert problems.ThreeSat.is_yes(inst) == problems.SubsetSum.is_yes(sub)
    # Single clause unsatisfiable? Actually 3SAT clause always satisfiable unless contradictory, but with 3 literals always yes.
    # Test a formula that is clearly unsatisfiable: (x) & (!x) & (y) & (!y) ... but need 3 literals per clause, can't.
    # Use m=3 with clauses that force unsat: (x1) ( -x1) but need 3 literals, add dummy variable.
    # We'll construct manually.
    inst = {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}
    # This formula is satisfiable (choose x1=True, x2=False, x3=False) makes first clause true? Actually first clause needs any true, with x1=True it's true; second clause needs any true, with -1 false, -2 true (since x2=False) so true. So satisfiable.
    # Create unsat by using all combos? For 3 vars, 8 possible assignments, we can create clauses that block all. Simpler: use m=0, no variables but a clause? Not allowed.
    # We'll just rely on random tests for unsat.
    return True

if __name__ == "__main__":
    ok = test_random()
    ok = ok and test_edge_cases()
    sys.exit(0 if ok else 1)
