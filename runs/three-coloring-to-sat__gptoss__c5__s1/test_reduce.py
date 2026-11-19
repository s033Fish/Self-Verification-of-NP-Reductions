import itertools
import json
import sys
from typing import List, Dict

from problems import ThreeColoring, Sat
from reduce import reduce as reduce_instance

# Import our brute-force solvers
from three_color_solver import solve as solve_three_color
from sat_solver import solve as solve_sat


def all_graphs(max_n: int) -> List[Dict]:
    instances = []
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
        # iterate over all subsets of possible_edges
        for r in range(len(possible_edges) + 1):
            for edges_subset in itertools.combinations(possible_edges, r):
                # convert to list of lists as required
                edges = [list(e) for e in edges_subset]
                instances.append({"n": n, "edges": edges})
    return instances


def main():
    max_n = 4  # small enough for exhaustive testing
    instances = all_graphs(max_n)
    total = len(instances)
    passed = 0
    for idx, inst in enumerate(instances):
        # Validate source instance
        ThreeColoring.validate(inst)
        # Solve source
        source_ans = solve_three_color(inst)
        # Reduce
        sat_inst = reduce_instance(inst)
        # Validate reduced instance
        Sat.validate(sat_inst)
        # Solve target
        target_ans = solve_sat(sat_inst)
        if source_ans == target_ans:
            passed += 1
        else:
            print(f"Mismatch on instance {idx}/{total}: {inst}")
            print(f"source answer={source_ans}, target answer={target_ans}")
            # exit early with failure
            sys.exit(1)
    # Write verdict
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
