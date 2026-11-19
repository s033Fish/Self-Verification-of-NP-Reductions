import json
import itertools
import sys
from typing import List, Dict

from problems import VertexCover, SetCover
from reduce import reduce as reduce_instance
from vertex_cover_solver import solve_vertex_cover
from set_cover_solver import solve_set_cover


def all_graph_instances(max_n: int = 4) -> List[Dict]:
    instances = []
    for n in range(max_n + 1):
        # generate all possible edges (u<v) for vertices 0..n-1
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        # all subsets of edges
        for r in range(len(possible_edges) + 1):
            for edges_subset in itertools.combinations(possible_edges, r):
                edges = [list(e) for e in edges_subset]
                # k values: from -1 to n+1 inclusive
                for k in range(-1, n + 2):
                    instance = {"n": n, "edges": edges, "k": k}
                    # validation ensures correctness
                    VertexCover.validate(instance)
                    instances.append(instance)
    return instances


def main():
    instances = all_graph_instances(4)
    total = len(instances)
    passed = 0
    for inst in instances:
        vc_ans = solve_vertex_cover(inst)
        reduced = reduce_instance(inst)
        # validate reduced instance
        SetCover.validate(reduced)
        sc_ans = solve_set_cover(reduced)
        if vc_ans == sc_ans:
            passed += 1
        else:
            print("Mismatch!", inst, reduced, vc_ans, sc_ans, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict, indent=2))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == "__main__":
    main()
