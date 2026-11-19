import json
import itertools
from typing import Dict, Any

from problems import Clique, IndependentSet
from reduce import reduce as reduce_instance
from solver import clique_solver, independent_set_solver


def generate_instances(max_n: int = 5):
    """Yield all possible Clique instances for n up to max_n.

    For each n we iterate over all subsets of the possible edges and over a
    range of k values covering edge cases.
    """
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
        # iterate over all edge subsets
        for mask in range(1 << len(possible_edges)):
            edges = []
            for i, (u, v) in enumerate(possible_edges):
                if mask & (1 << i):
                    edges.append([u, v])
            # k values: include negative, zero, 1..n+1
            ks = list(range(-1, n + 2))
            for k in ks:
                instance = {"n": n, "edges": edges, "k": k}
                # validation may raise, but our generation respects constraints
                yield instance


def main():
    total = 0
    passed = 0
    for src in generate_instances(5):
        total += 1
        # compute answers using brute solvers
        src_answer = clique_solver(src)
        # reduce
        try:
            tgt = reduce_instance(src)
        except Exception as e:
            # reduction raised error -> fail
            continue
        tgt_answer = independent_set_solver(tgt)
        if src_answer == tgt_answer:
            passed += 1
        else:
            # debug output could be printed, but we just count failures
            pass
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == "__main__":
    main()
