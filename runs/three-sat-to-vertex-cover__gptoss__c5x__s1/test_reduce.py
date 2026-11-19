"""Independent brute-force check of reduce.py (3-SAT -> Vertex Cover).

We implement our own solvers for both problems directly from the
definitions in problems.py, generate many small source instances, apply
reduce.reduce, and compare answers.
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from typing import Dict, List, Optional

from problems import ThreeSat, VertexCover, InvalidInstance
from reduce import reduce

sys.setrecursionlimit(100000)


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.
# ----------------------------------------------------------------------

def solve_three_sat(instance: Dict) -> bool:
    """True iff the 3-SAT instance is satisfiable (brute force 2^m)."""
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    if not clauses:
        return True
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def min_vertex_cover(n: int, edges: List[List[int]]) -> int:
    """Exact minimum vertex cover size via recursive branching.

    Pick an uncovered edge (u, v); any cover must contain u or v, so
    min = 1 + min(solve with u removed, solve with v removed).
    Memoised on the remaining edge set.
    """
    memo: Dict[frozenset, int] = {}

    def rec(rem: frozenset) -> int:
        if not rem:
            return 0
        cached = memo.get(rem)
        if cached is not None:
            return cached
        u, v = next(iter(rem))
        rem_u = frozenset(e for e in rem if u not in e)
        rem_v = frozenset(e for e in rem if v not in e)
        res = 1 + min(rec(rem_u), rec(rem_v))
        memo[rem] = res
        return res

    return rec(frozenset(tuple(e) for e in edges))


def solve_vertex_cover(instance: Dict) -> bool:
    """True iff graph has a vertex cover of size <= k."""
    VertexCover.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    return min_vertex_cover(n, edges) <= k


# ----------------------------------------------------------------------
# Instance generation.
# ----------------------------------------------------------------------

def gen_instance(rng: random.Random, m: int, n_clauses: int) -> Optional[Dict]:
    """Random 3-SAT instance with m vars and n_clauses clauses.

    Returns None when the request is impossible (m < 3 with clauses).
    Duplicate clauses are allowed by the definition.
    """
    if n_clauses == 0:
        return {"num_vars": m, "clauses": []}
    if m < 3:
        return None
    clauses: List[List[int]] = []
    for _ in range(n_clauses):
        vars_ = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vars_]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_instances():
    """Exhaustively enumerate tiny instances (m in 0..3, up to 2 clauses)."""
    yield {"num_vars": 0, "clauses": []}
    for m in range(1, 4):
        var_triples = list(itertools.combinations(range(1, m + 1), 3))
        clause_pool = []
        for trip in var_triples:
            for signs in itertools.product((1, -1), repeat=3):
                clause_pool.append([s * v for s, v in zip(signs, trip)])
        yield {"num_vars": m, "clauses": []}
        for c in clause_pool:
            yield {"num_vars": m, "clauses": [list(c)]}
        for c1 in clause_pool:
            for c2 in clause_pool:
                yield {"num_vars": m, "clauses": [list(c1), list(c2)]}


def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst: Dict, label: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            src_ans = solve_three_sat(inst)
            target = reduce(inst)
            VertexCover.validate(target)  # reduction must emit valid target
            tgt_ans = solve_vertex_cover(target)
            if src_ans == tgt_ans:
                tests_passed += 1
            else:
                failures.append((label, inst, src_ans, target, tgt_ans))
        except Exception as exc:  # noqa: BLE001
            failures.append((label, inst, "EXC", repr(exc), None))

    # 1. Exhaustive tiny instances
    for inst in all_small_instances():
        check(inst, "exhaustive")

    # 2. Random instances, including no-clause and m=0 edge cases
    rng = random.Random(12345)
    for m in range(0, 6):
        for n_clauses in range(0, 5):
            for _ in range(30):
                inst = gen_instance(rng, m, n_clauses)
                if inst is not None:
                    check(inst, "random")

    # 3. Explicit edge cases from the definitions
    check({"num_vars": 0, "clauses": []}, "edge: m=0 no clauses")
    check({"num_vars": 5, "clauses": []}, "edge: no clauses m=5")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "edge: single clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "edge: duplicate clause")
    all_clauses = []
    for signs in itertools.product((1, -1), repeat=3):
        all_clauses.append([s * v for s, v in zip(signs, (1, 2, 3))])
    check({"num_vars": 3, "clauses": all_clauses}, "edge: unsatisfiable 3-var")

    # 4. Malformed source instances must be rejected by validation
    malformed = [
        {"num_vars": -1, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2]]},       # 2 literals
        {"num_vars": 3, "clauses": [[1, 1, 2]]},    # repeated variable
        {"num_vars": 3, "clauses": [[1, -1, 2]]},   # both v and -v
        {"num_vars": 3, "clauses": [[1, 2, 4]]},    # out of range
        {"num_vars": 3, "clauses": [[1, 2, 0]]},    # literal 0
        {"num_vars": 3},                             # missing key
    ]
    for inst in malformed:
        tests_run += 1
        try:
            reduce(inst)
            failures.append(("malformed-not-rejected", inst, None, None, None))
        except InvalidInstance:
            tests_passed += 1
        except Exception as exc:  # noqa: BLE001
            failures.append(("malformed-wrong-exc", inst, repr(exc), None, None))

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:20]:
        print("FAIL:", f)

    verified = (tests_run > 0 and tests_passed == tests_run and not failures)
    with open("verdict.json", "w") as fh:
        json.dump({"verified": verified, "tests_run": tests_run,
                   "tests_passed": tests_passed}, fh)
    print("verdict:", {"verified": verified, "tests_run": tests_run,
                       "tests_passed": tests_passed})


if __name__ == "__main__":
    main()
