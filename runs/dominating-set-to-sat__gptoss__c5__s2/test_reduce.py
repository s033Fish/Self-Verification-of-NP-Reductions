import json
import itertools
import sys

from problems import DominatingSet, Sat
from reduce import reduce
from solve_bruteforce import solve_dominating_set, solve_sat


def generate_graphs(n):
    vertices = list(range(n))
    possible_edges = list(itertools.combinations(vertices, 2))
    for mask in range(1 << len(possible_edges)):
        edges = []
        for i, (u, v) in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append([u, v])
        yield edges


def run_tests(max_n=4):
    total = 0
    passed = 0
    for n in range(max_n + 1):
        for edges in generate_graphs(n):
            for k in range(-1, n + 2):  # include some out of range values
                instance = {"n": n, "edges": edges, "k": k}
                # validate source instance
                try:
                    DominatingSet.validate(instance)
                except Exception as e:
                    print("Invalid source instance", instance, e)
                    continue
                # compute expected answer
                expected = solve_dominating_set(instance)
                # reduce
                reduced = reduce(instance)
                # validate reduced instance
                try:
                    Sat.validate(reduced)
                except Exception as e:
                    print("Invalid reduced instance", reduced, e)
                    continue
                # compute reduced answer
                got = solve_sat(reduced)
                total += 1
                if expected == got:
                    passed += 1
                else:
                    print("Mismatch!", instance, "expected", expected, "got", got)
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    result = {"verified": total == passed, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
