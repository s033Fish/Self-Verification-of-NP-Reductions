import itertools
import json
import sys
from typing import Dict, List

from hpath_solver import solve as hpath_solve
from sat_solver import solve as sat_solve
from reduce import reduce as reduce_instance


def all_graphs(n: int) -> List[Dict]:
    verts = list(range(n))
    possible_edges = list(itertools.combinations(verts, 2))
    graphs = []
    for r in range(len(possible_edges) + 1):
        for combo in itertools.combinations(possible_edges, r):
            # convert to list of [u,v]
            edges = [list(e) for e in combo]
            graphs.append({"n": n, "edges": edges})
    return graphs


def run_tests(max_n: int = 4) -> dict:
    total = 0
    passed = 0
    for n in range(max_n + 1):
        for g in all_graphs(n):
            total += 1
            hp_ans = hpath_solve(g)
            sat_instance = reduce_instance(g)
            sat_ans = sat_solve(sat_instance)
            if hp_ans == sat_ans:
                passed += 1
            else:
                print("Mismatch!", g, "hp", hp_ans, "sat", sat_ans, file=sys.stderr)
                # break early for debugging
                # return {"total": total, "passed": passed}
    return {"total": total, "passed": passed}

if __name__ == "__main__":
    result = run_tests()
    print(json.dumps(result))
    # write verdict.json
    verdict = {
        "verified": result["total"] == result["passed"],
        "tests_run": result["total"],
        "tests_passed": result["passed"],
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('Verdict written to verdict.json')
