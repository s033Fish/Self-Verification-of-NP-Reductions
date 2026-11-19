import json
import itertools
from problems import ThreeColoring, OneInThreeSat
from reduce import reduce
from solvers import solve_three_coloring, solve_one_in_three_sat


def all_graphs(max_n: int, max_edges: int | None = None):
    """Yield graph instances up to max_n vertices.
    If max_edges is set, only yield graphs with at most that many edges.
    """
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
        for r in range(len(possible_edges) + 1):
            if max_edges is not None and r > max_edges:
                continue
            for edges in itertools.combinations(possible_edges, r):
                yield {"n": n, "edges": [[u, v] for u, v in edges]}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []
    # Small graphs up to 3 vertices (all edges)
    for instance in all_graphs(3):
        ThreeColoring.validate(instance)
        src_ans = solve_three_coloring(instance)
        reduced = reduce(instance)
        OneInThreeSat.validate(reduced)
        tgt_ans = solve_one_in_three_sat(reduced)
        tests_run += 1
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            failures.append({"instance": instance, "src_ans": src_ans, "tgt_ans": tgt_ans})
    # Additional graphs with 4 vertices but at most 2 edges (keep SAT tractable)
    for instance in all_graphs(4, max_edges=2):
        ThreeColoring.validate(instance)
        src_ans = solve_three_coloring(instance)
        reduced = reduce(instance)
        OneInThreeSat.validate(reduced)
        # quick guard: if SAT instance would be huge, skip (variables > 20)
        if reduced["num_vars"] > 20:
            continue
        tgt_ans = solve_one_in_three_sat(reduced)
        tests_run += 1
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            failures.append({"instance": instance, "src_ans": src_ans, "tgt_ans": tgt_ans})
    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))
    if failures:
        print("Failures:")
        for f in failures:
            print(json.dumps(f, indent=2))
        raise SystemExit(1)

if __name__ == "__main__":
    main()
