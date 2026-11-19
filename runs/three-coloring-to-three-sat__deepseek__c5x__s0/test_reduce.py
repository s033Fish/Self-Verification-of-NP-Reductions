import json
import itertools
from problems import ThreeColoring, ThreeSat
from reduce import reduce as reduce_instance
from solve_bruteforce import solve_three_coloring, solve_three_sat


def all_graph_instances(max_n=4):
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [(i, j) for i in vertices for j in vertices if i < j]
        # iterate over all subsets of possible_edges
        for r in range(len(possible_edges) + 1):
            for edges in itertools.combinations(possible_edges, r):
                instance = {"n": n, "edges": [list(e) for e in edges]}
                yield instance


def main():
    total = 0
    passed = 0
    for instance in all_graph_instances():
        total += 1
        # Validate source
        ThreeColoring.validate(instance)
        source_ans = solve_three_coloring(instance)
        # Reduce
        reduced = reduce_instance(instance)
        # Validate target
        ThreeSat.validate(reduced)
        target_ans = solve_three_sat(reduced)
        if source_ans == target_ans:
            passed += 1
        else:
            print("Mismatch!", instance, "source", source_ans, "target", target_ans)
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
