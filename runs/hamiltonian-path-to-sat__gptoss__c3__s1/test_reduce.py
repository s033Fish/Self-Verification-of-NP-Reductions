import itertools
import random
import sys

from problems import HamiltonianPath, Sat
from reduce import reduce


def test_all_graphs(max_n=4):
    total = 0
    passed = 0
    for n in range(max_n + 1):
        # generate all edge subsets
        vertices = list(range(n))
        all_pairs = list(itertools.combinations(vertices, 2))
        for mask in range(1 << len(all_pairs)):
            edges = []
            for idx, (u, v) in enumerate(all_pairs):
                if mask >> idx & 1:
                    edges.append([u, v])
            instance = {"n": n, "edges": edges}
            # validate
            HamiltonianPath.validate(instance)
            # reduce
            sat_inst = reduce(instance)
            Sat.validate(sat_inst)
            # compare answers
            hp_yes = HamiltonianPath.is_yes(instance)
            sat_yes = Sat.is_yes(sat_inst)
            total += 1
            if hp_yes == sat_yes:
                passed += 1
            else:
                print("Mismatch!", instance, "hp", hp_yes, "sat", sat_yes, file=sys.stderr)
                return total, passed
    return total, passed

if __name__ == "__main__":
    total, passed = test_all_graphs(4)
    print(f"Tests run: {total}, passed: {passed}")
    import json
    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    if total != passed:
        sys.exit(1)
