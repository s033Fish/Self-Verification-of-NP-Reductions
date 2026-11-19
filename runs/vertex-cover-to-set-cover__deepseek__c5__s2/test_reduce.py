"""Independent verification of reduce.py for VertexCover -> SetCover.

We implement brute-force solvers for both problems straight from the
definitions in problems.py, then compare answers on many small source
instances against the answers of their reductions.  We also cross-check our
solvers against independently written alternatives (max independent set for
Vertex Cover, bitmask union for Set Cover), check that reduce does not mutate
its input, and check the reduction runs fast on a large instance.
"""

from __future__ import annotations

import copy
import itertools
import random
import time

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)
# ----------------------------------------------------------------------

def solve_vertex_cover(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    # A cover of size <= k exists iff one of size exactly t exists for some
    # t in 0..min(k, n).  Enumerate all vertex subsets up to that size.
    for t in range(0, min(k, n) + 1):
        for chosen in itertools.combinations(range(n), t):
            chosen_set = set(chosen)
            covered = 0
            for u, v in edges:
                if u in chosen_set or v in chosen_set:
                    covered += 1
            if covered == len(edges):
                return True
    return False


def solve_set_cover(instance: dict) -> bool:
    u = instance["universe_size"]
    sets = instance["sets"]
    k = instance["k"]
    if k < 0:
        return False
    m = len(sets)
    for t in range(0, min(k, m) + 1):
        for chosen in itertools.combinations(range(m), t):
            union = set()
            for idx in chosen:
                union.update(sets[idx])
            if len(union) == u:
                return True
    return False


# ----------------------------------------------------------------------
# Independent alternative solvers used only as cross-checks
# ----------------------------------------------------------------------

def solve_vc_independent(instance: dict) -> bool:
    """min vertex cover = n - max independent set."""
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k < 0:
        return False
    best = 0
    for mask in range(1 << n):
        indep = True
        for u, v in edges:
            if (mask >> u) & 1 and (mask >> v) & 1:
                indep = False
                break
        if indep:
            best = max(best, bin(mask).count("1"))
    return n - best <= k


def solve_sc_bitmask(instance: dict) -> bool:
    """Set cover via bitmask unions over the universe."""
    u, sets, k = instance["universe_size"], instance["sets"], instance["k"]
    if k < 0:
        return False
    masks = []
    for s in sets:
        m = 0
        for e in s:
            m |= 1 << e
        masks.append(m)
    full = (1 << u) - 1
    m = len(masks)
    for t in range(0, min(k, m) + 1):
        for combo in itertools.combinations(masks, t):
            acc = 0
            for x in combo:
                acc |= x
            if acc == full:
                return True
    return False


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def all_vertex_cover_instances(max_n: int = 4):
    """Every valid VertexCover instance with n <= max_n and k spanning the
    interesting boundaries."""
    for n in range(0, max_n + 1):
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for r in range(len(possible) + 1):
            for edge_subset in itertools.combinations(possible, r):
                edges = [list(e) for e in edge_subset]
                for k in range(-1, n + 2):
                    yield {"n": n, "edges": edges, "k": k}


def random_vertex_cover_instances(count: int = 2000, seed: int = 0):
    rng = random.Random(seed)
    for _ in range(count):
        n = rng.randint(0, 6)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        rng.shuffle(possible)
        r = rng.randint(0, len(possible))
        edges = [list(e) for e in possible[:r]]
        k = rng.randint(-2, n + 2)
        yield {"n": n, "edges": edges, "k": k}


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

class Counter:
    def __init__(self):
        self.run = 0
        self.passed = 0

    def check(self, ok: bool, context: str) -> None:
        self.run += 1
        if ok:
            self.passed += 1
        else:
            print("FAIL:", context)


def check_reduction(instance: dict, c: Counter) -> None:
    SOURCE.validate(instance)
    snapshot = copy.deepcopy(instance)
    target = reduce(instance)
    TARGET.validate(target)
    c.check(instance == snapshot, f"reduce mutated input {instance!r}")
    src_ans = solve_vertex_cover(instance)
    tgt_ans = solve_set_cover(target)
    c.check(
        src_ans == tgt_ans,
        f"answer mismatch source={instance!r} ({src_ans}) target={target!r} ({tgt_ans})",
    )


def main() -> None:
    c = Counter()

    for instance in all_vertex_cover_instances(max_n=4):
        check_reduction(instance, c)

    for instance in random_vertex_cover_instances(count=2000, seed=12345):
        check_reduction(instance, c)

    # Structured larger cases: complete, empty, path, matching.
    for n in range(5, 9):
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        families = {
            "complete": [list(e) for e in possible],
            "empty": [],
            "path": [[i, i + 1] for i in range(n - 1)],
            "matching": [[i, i + 1] for i in range(0, n - 1, 2)],
        }
        for edges in families.values():
            for k in range(-1, n + 2):
                check_reduction({"n": n, "edges": edges, "k": k}, c)

    # Cross-check our brute-force solvers against independent formulations.
    rng = random.Random(7)
    for _ in range(3000):
        n = rng.randint(0, 6)
        poss = [(a, b) for a in range(n) for b in range(a + 1, n)]
        rng.shuffle(poss)
        edges = [list(e) for e in poss[: rng.randint(0, len(poss))]]
        k = rng.randint(-2, n + 2)
        inst = {"n": n, "edges": edges, "k": k}
        c.check(
            solve_vertex_cover(inst) == solve_vc_independent(inst),
            f"VC solver disagreement on {inst!r}",
        )
        tgt = reduce(inst)
        c.check(
            solve_set_cover(tgt) == solve_sc_bitmask(tgt),
            f"SC solver disagreement on {tgt!r}",
        )

    # Polynomial-time / scaling sanity check.
    n = 2000
    edges = [[i, i + 1] for i in range(n - 1)]
    big = {"n": n, "edges": edges, "k": n}
    t0 = time.time()
    big_tgt = reduce(big)
    elapsed = time.time() - t0
    TARGET.validate(big_tgt)
    c.check(big_tgt["universe_size"] == len(edges), "wrong universe size on big instance")
    c.check(elapsed < 5.0, f"reduce too slow on big instance: {elapsed:.3f}s")

    print(f"tests_run={c.run} tests_passed={c.passed}")
    assert c.run == c.passed, "some tests failed"


if __name__ == "__main__":
    main()
