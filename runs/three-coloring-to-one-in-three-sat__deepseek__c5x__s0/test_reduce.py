import json
import random
import sys
from pathlib import Path

# Import modules
import problems
import reduce
from solve_bruteforce import solve_three_coloring, solve_one_in_three_sat

def generate_random_graph(max_n=5):
    n = random.randint(0, max_n)
    # generate all possible edges without self-loops
    possible = [(u, v) for u in range(n) for v in range(u+1, n)]
    edges = []
    for u, v in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    return {"n": n, "edges": edges}

def generate_k4():
    # K4 on vertices 0..3
    n = 4
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            edges.append([u, v])
    return {"n": n, "edges": edges}

def run_test(instance):
    # validate source instance
    problems.ThreeColoring.validate(instance)
    # reduce
    reduced = reduce.reduce(instance)
    # validate target instance (positive only)
    problems.OneInThreeSat.validate(reduced)
    # solve both
    ans_src = solve_three_coloring(instance)
    ans_tgt = solve_one_in_three_sat(reduced)
    return ans_src == ans_tgt

def main():
    total = 0
    passed = 0
    # deterministic seed for reproducibility
    random.seed(0)
    # test many random graphs
    for _ in range(200):
        inst = generate_random_graph()
        total += 1
        if run_test(inst):
            passed += 1
    # test edge cases
    edge_cases = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": []},
        {"n": 3, "edges": []},
        generate_k4(),
    ]
    for inst in edge_cases:
        total += 1
        if run_test(inst):
            passed += 1
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path('verdict.json').write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))
    sys.exit(0 if verdict["verified"] else 1)

if __name__ == '__main__':
    main()
