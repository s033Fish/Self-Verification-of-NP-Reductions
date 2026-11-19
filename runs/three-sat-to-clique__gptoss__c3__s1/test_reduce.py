import random
import sys
import traceback

from problems import ThreeSat, Clique
from reduce import reduce


def run_tests(num_trials=200):
    rng = random.Random(0)
    passed = 0
    total = 0
    # test random instances with variable count up to 4
    for scale in range(0, 5):
        for _ in range(num_trials):
            inst = ThreeSat.random_instance(rng, scale)
            # validate
            ThreeSat.validate(inst)
            # reduce
            try:
                clique_inst = reduce(inst)
                Clique.validate(clique_inst)
            except Exception as e:
                print("Reduction raised on instance", inst)
                traceback.print_exc()
                return False, total
            # compare answers
            ans_sat = ThreeSat.is_yes(inst)
            ans_clique = Clique.is_yes(clique_inst)
            if ans_sat != ans_clique:
                print("Mismatch!", inst, "->", clique_inst, ans_sat, ans_clique)
                return False, total
            passed += 1
            total += 1
    # also test explicit edge cases
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
    ]
    for inst in edge_cases:
        ThreeSat.validate(inst)
        clique_inst = reduce(inst)
        Clique.validate(clique_inst)
        if ThreeSat.is_yes(inst) != Clique.is_yes(clique_inst):
            print("Edge case mismatch", inst, clique_inst)
            return False, total
        passed += 1
        total += 1
    return True, total

if __name__ == "__main__":
    ok, total = run_tests()
    if ok:
        print(f"All {total} tests passed.")
        sys.exit(0)
    else:
        print(f"Tests failed after {total} cases.")
        sys.exit(1)
