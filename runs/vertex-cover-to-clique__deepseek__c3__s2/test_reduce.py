import itertools
import random

import problems
from problems import SOURCE, TARGET
from reduce import reduce


def check(instance, results):
    """Compare source and reduced target answers; validate the reduction."""
    out = reduce(instance)
    TARGET.validate(out)
    got = TARGET.is_yes(out)
    want = SOURCE.is_yes(instance)
    results["run"] += 1
    if got == want:
        results["passed"] += 1
    else:
        results["failures"].append((instance, out, want, got))


def main():
    results = {"run": 0, "passed": 0, "failures": []}

    # Exhaustive over all graphs with up to 4 vertices, all k in -2..n+2.
    for n in range(0, 5):
        for edges in problems.all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k}, results)

    # Exhaustive over all graphs with 5 vertices, a few k values.
    for edges in problems.all_graphs(5):
        for k in range(-1, 7):
            check({"n": 5, "edges": edges, "k": k}, results)

    # Randomised larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 9)
        edges = problems.random_graph(rng, n)
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k}, results)

    # Random instances from the problem's own generator.
    for scale in range(0, 5):
        for _ in range(200):
            inst = SOURCE.random_instance(rng, scale)
            check(inst, results)

    # Explicit edge cases.
    edge_cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -1},
        {"n": 0, "edges": [], "k": 5},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": -1},
        {"n": 3, "edges": [], "k": 3},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 1},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": -1},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 10},
        {"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]], "k": 1},
        {"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]], "k": 0},
    ]
    for inst in edge_cases:
        check(inst, results)

    print(f"tests_run={results['run']} tests_passed={results['passed']}")
    for failure in results["failures"][:10]:
        print("FAIL", failure)
    assert not results["failures"], "some reductions disagreed"

    with open("verdict.json", "w") as fh:
        import json

        json.dump(
            {
                "verified": True,
                "tests_run": results["run"],
                "tests_passed": results["passed"],
            },
            fh,
        )
    print("verdict.json written")


if __name__ == "__main__":
    main()
