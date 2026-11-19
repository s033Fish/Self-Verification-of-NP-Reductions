"""Test the reduction from HamiltonianPath to HamiltonianCycle.

The script implements exhaustive brute‑force solvers for both problems for
small graphs (n ≤ 5). For every possible undirected simple graph it checks
that ``reduce`` produces a target instance whose answer matches the source
instance answer.

The script is deliberately self‑contained – it does not rely on any external
testing framework. It prints a short summary and writes ``verdict.json``
containing the verification result required by the task description.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce as reduce_instance


def hamiltonian_path_bruteforce(instance: dict) -> bool:
    """Return True iff the given instance has a Hamiltonian path.

    The implementation follows the definition in ``problems.py`` exactly.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}

    # Edge cases from the specification
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        return frozenset((0, 1)) in edges

    # General case: try every permutation of vertices.
    for perm in itertools.permutations(range(n)):
        ok = True
        for a, b in zip(perm, perm[1:]):
            if frozenset((a, b)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def hamiltonian_cycle_bruteforce(instance: dict) -> bool:
    """Return True iff the given instance has a Hamiltonian cycle.

    Mirrors the definition in ``problems.py``.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}

    if n <= 2:
        return False
    if n == 3:
        # Only a triangle qualifies.
        return all(frozenset(pair) in edges for pair in [(0, 1), (1, 2), (2, 0)])

    # General case: check all permutations (fix first vertex to reduce symmetry).
    for perm in itertools.permutations(range(n)):
        # Ensure we count each cycle multiple times – correctness only matters.
        ok = True
        for a, b in zip(perm, perm[1:]):
            if frozenset((a, b)) not in edges:
                ok = False
                break
        # check edge from last back to first
        if ok and frozenset((perm[-1], perm[0])) in edges:
            return True
    return False


def all_graphs_up_to(max_n: int):
    """Yield every simple undirected graph with vertices 0..n-1 for n ≤ max_n.

    Each yielded value is a dict compatible with ``problems`` definitions.
    """
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [list(e) for e in itertools.combinations(vertices, 2)]
        for subset_mask in range(1 << len(possible_edges)):
            edges = [possible_edges[i] for i in range(len(possible_edges)) if (subset_mask >> i) & 1]
            yield {"n": n, "edges": edges}


def main() -> None:
    total = 0
    passed = 0
    for instance in all_graphs_up_to(5):
        total += 1
        # Validate source instance (should never raise).
        HamiltonianPath.validate(instance)
        src_ans = hamiltonian_path_bruteforce(instance)
        # Reduce and validate target instance.
        target_instance = reduce_instance(instance)
        HamiltonianCycle.validate(target_instance)
        tgt_ans = hamiltonian_cycle_bruteforce(target_instance)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch found!", file=sys.stderr)
            print("Source instance:", json.dumps(instance), file=sys.stderr)
            print("Source answer:", src_ans, file=sys.stderr)
            print("Reduced target instance:", json.dumps(target_instance), file=sys.stderr)
            print("Target answer:", tgt_ans, file=sys.stderr)
            # Stop early – the verdict will be false.
            break

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))
    # Exit code 0 if verified, 1 otherwise (useful for CI).
    sys.exit(0 if verdict["verified"] else 1)


if __name__ == "__main__":
    main()

