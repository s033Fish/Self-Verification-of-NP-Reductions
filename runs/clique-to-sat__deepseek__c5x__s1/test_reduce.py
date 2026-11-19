import json
import itertools
import os
import sys

# Ensure the working directory is in path
sys.path.append(os.path.abspath('.'))

from problems import Clique, Sat
from reduce import reduce as reduce_func
from solve_bruteforce import solve_clique, solve_sat


def generate_instances(max_n=4):
    instances = []
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = list(itertools.combinations(vertices, 2))
        # all subsets of possible edges
        for edge_subset in itertools.chain.from_iterable(
            itertools.combinations(possible_edges, r) for r in range(len(possible_edges) + 1)
        ):
            edges = [list(e) for e in edge_subset]
            for k in range(-1, n + 2):  # include values below 0 and above n
                instance = {"n": n, "edges": edges, "k": k}
                instances.append(instance)
    return instances


def main():
    instances = generate_instances()
    total = len(instances)
    passed = 0
    failures = []
    for idx, inst in enumerate(instances):
        try:
            Clique.validate(inst)
        except Exception as e:
            failures.append((idx, "validation", str(e)))
            continue
        # compute expected answer
        expected = solve_clique(inst)
        # reduce
        reduced = reduce_func(inst)
        try:
            Sat.validate(reduced)
        except Exception as e:
            failures.append((idx, "reduced_validation", str(e)))
            continue
        got = solve_sat(reduced)
        if expected == got:
            passed += 1
        else:
            failures.append((idx, "mismatch", (expected, got, inst, reduced)))
    # write verdict
    verdict = {
        "verified": len(failures) == 0,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    # also output summary
    print(json.dumps(verdict, indent=2))
    if failures:
        print("Failures:", file=sys.stderr)
        for f in failures:
            print(f, file=sys.stderr)

if __name__ == "__main__":
    main()
