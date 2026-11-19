"""Compare brute-force answers on many small Vertex Cover instances and their
reductions to Independent Set."""

from __future__ import annotations

from itertools import combinations

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import independent_set_yes, vertex_cover_yes


def all_graphs(n):
    """All simple undirected graphs on vertices 0..n-1."""
    possible = list(combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if mask >> i & 1]
        yield edges


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    for n in range(0, 6):
        for edges in all_graphs(n):
            # cover a range of k values including negatives and beyond n
            for k in range(-2, n + 3):
                src = {"n": n, "edges": [list(e) for e in edges], "k": k}
                SOURCE.validate(src)
                tgt = reduce(src)
                TARGET.validate(tgt)

                expected = vertex_cover_yes(src)
                got = independent_set_yes(tgt)
                tests_run += 1
                if expected == got:
                    tests_passed += 1
                else:
                    failures.append((src, tgt, expected, got))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        for f in failures[:10]:
            print("FAIL:", f)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
