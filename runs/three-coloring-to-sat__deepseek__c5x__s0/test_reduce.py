"""Automated tests for the reduction from ThreeColoring to SAT.

The repository provides a ``reduce`` function that maps a ThreeColoring
instance to a SAT instance.  This test suite implements straightforward
brute‑force solvers for both problems and checks that the answer of the
reduced SAT instance matches the answer of the original graph instance
for a large collection of small graphs.

If all tests pass we write ``verdict.json`` with ``verified: true``;
otherwise ``verified`` is false.  The file also records the total number
of tests run and how many passed.
"""

from __future__ import annotations

import json
import itertools
import sys
from pathlib import Path

# Import the reduction implementation and the problem definitions.
from reduce import reduce as reduce_instance
from problems import ThreeColoring, Sat


def three_coloring_bruteforce(instance: dict) -> bool:
    """Return True iff the given graph is 3‑colorable.

    The instance follows the format defined in ``ThreeColoring``:
    ``{"n": int, "edges": [[u, v], ...]}``.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    # Edge case: n == 0 is trivially yes.
    if n == 0:
        return True
    # Try all colour assignments (3^n possibilities). For n up to 6 this
    # is at most 729 assignments which is negligible.
    for assignment in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if assignment[u] == assignment[v]:
                ok = False
                break
        if ok:
            return True
    return False


def sat_bruteforce(instance: dict) -> bool:
    """Return True iff the given CNF formula is satisfiable.

    The instance follows the format defined in ``Sat``:
    ``{"num_vars": m, "clauses": [[lit, ...], ...]}`` where a literal
    is an integer ``+v`` (true) or ``-v`` (false). An empty clause is
    unsatisfiable; a formula with no clauses is satisfiable.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # If there is an empty clause the formula is unsatisfiable.
    if any(len(clause) == 0 for clause in clauses):
        return False
    # No clauses -> trivially satisfiable.
    if not clauses:
        return True
    # Enumerate all 2^m assignments.
    for bits in range(1 << m):
        # bits's i‑th bit corresponds to variable i+1 being True.
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def generate_all_graphs(max_n: int) -> list[dict]:
    """Generate every simple undirected graph with up to ``max_n`` vertices.

    For each ``n`` we iterate over all subsets of the possible edges.
    ``max_n`` is kept small (≤5) so the total number of graphs is
    manageable.
    """
    graphs: list[dict] = []
    for n in range(max_n + 1):
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(possible_edges)):
            edges = []
            for i, (u, v) in enumerate(possible_edges):
                if mask & (1 << i):
                    edges.append([u, v])
            graphs.append({"n": n, "edges": edges})
    return graphs


def main() -> None:
    # Validate that the problem definitions accept the format.
    # (Any malformed instance would raise, which we treat as a failure.)
    all_graphs = generate_all_graphs(5)
    total = len(all_graphs)
    passed = 0
    for idx, graph in enumerate(all_graphs, 1):
        try:
            ThreeColoring.validate(graph)
        except Exception as e:
            print(f"Invalid source instance #{idx}: {e}", file=sys.stderr)
            continue
        source_ans = three_coloring_bruteforce(graph)
        # Reduce and validate target instance.
        sat_instance = reduce_instance(graph)
        try:
            Sat.validate(sat_instance)
        except Exception as e:
            print(f"Invalid reduced instance #{idx}: {e}", file=sys.stderr)
            continue
        target_ans = sat_bruteforce(sat_instance)
        if source_ans == target_ans:
            passed += 1
        else:
            print(
                f"Mismatch on graph #{idx} (n={graph['n']}, edges={graph['edges']})",
                file=sys.stderr,
            )
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
