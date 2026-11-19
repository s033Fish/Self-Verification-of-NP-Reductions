"""Independent brute-force tests for reduce.py (Vertex Cover -> Dominating Set)."""
from itertools import combinations

from problems import VertexCover, DominatingSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def vertex_cover_yes(instance):
    """True iff graph has a vertex cover of size AT MOST k."""
    VertexCover.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    # No edges: empty set covers, yes for k >= 0.
    # k >= n: all vertices cover every edge.
    if k >= n:
        return True
    for size in range(0, k + 1):
        for subset in combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def dominating_set_yes(instance):
    """True iff graph has a dominating set of size AT MOST k."""
    DominatingSet.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(0, k + 1):
        for subset in combinations(range(n), size):
            chosen = set(subset)
            dominated = set(chosen)
            for v in chosen:
                dominated |= adj[v]
            if len(dominated) == n:
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation: all simple graphs on n vertices, various k.

def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield edges


def source_instances(max_n=5):
    for n in range(0, max_n + 1):
        for edges in all_graphs(n):
            for k in range(-1, n + 2):
                yield {"n": n, "edges": edges, "k": k}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []
    for inst in source_instances(5):
        tests_run += 1
        src_yes = vertex_cover_yes(inst)
        red = reduce(inst)
        DominatingSet.validate(red)
        tgt_yes = dominating_set_yes(red)
        if src_yes == tgt_yes:
            tests_passed += 1
        else:
            if len(failures) < 10:
                failures.append((inst, src_yes, red, tgt_yes))
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for inst, sy, red, ty in failures:
        print("FAIL src_yes=%s red_yes=%s" % (sy, ty))
        print("   src:", inst)
        print("   red:", red)
    return tests_run, tests_passed


if __name__ == "__main__":
    main()

def write_verdict():
    import json
    tests_run, tests_passed = main()
    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)


if __name__ == "__main__":
    write_verdict()
