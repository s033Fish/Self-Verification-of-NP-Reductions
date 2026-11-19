"""Independent brute-force check of reduce.py (HamiltonianPath -> HamiltonianCycle)."""
from itertools import combinations, permutations

from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce


def has_ham_path(n, edges):
    """Brute force: is there a simple path visiting every vertex exactly once?"""
    if n == 0:
        return False
    if n == 1:
        return True
    adj = {v: set() for v in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # DFS over simple paths
    def dfs(v, visited):
        if len(visited) == n:
            return True
        for w in adj[v]:
            if w not in visited:
                visited.add(w)
                if dfs(w, visited):
                    return True
                visited.remove(w)
        return False
    for start in range(n):
        if dfs(start, {start}):
            return True
    return False


def has_ham_cycle(n, edges):
    """Brute force: is there a cycle visiting every vertex exactly once?"""
    if n <= 2:
        return False
    adj = {v: set() for v in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # fix start = 0, try orderings of the remaining vertices
    for perm in permutations(range(1, n)):
        order = (0,) + perm
        ok = True
        for i in range(n):
            a = order[i]
            b = order[(i + 1) % n]
            if b not in adj[a]:
                ok = False
                break
        if ok:
            return True
    return False


def all_graphs(n):
    pairs = list(combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask & (1 << i)]
        yield {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []
    for n in range(0, 7):
        for inst in all_graphs(n):
            tests_run += 1
            src_ans = has_ham_path(inst["n"], inst["edges"])
            red = reduce(inst)
            # reduced instance must be a valid target instance
            try:
                HamiltonianCycle.validate(red)
            except Exception as e:  # noqa
                failures.append((inst, red, "invalid target instance: %r" % (e,)))
                continue
            tgt_ans = has_ham_cycle(red["n"], red["edges"])
            if src_ans == tgt_ans:
                tests_passed += 1
            else:
                failures.append((inst, red, "src=%s tgt=%s" % (src_ans, tgt_ans)))

    print("tests_run=%d tests_passed=%d failures=%d" % (tests_run, tests_passed, len(failures)))
    for f in failures[:20]:
        print("FAIL:", f)

    # Also check that malformed input is rejected.
    for bad in [{"n": 2, "edges": [[0, 1], [1, 0]]},
                {"n": 2, "edges": [[0, 0]]},
                {"n": 2, "edges": [[0, 2]]},
                {"n": -1, "edges": []}]:
        try:
            reduce(bad)
            print("FAIL: malformed input accepted:", bad)
        except Exception:
            pass

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    tests_run, tests_passed, failures = main()
    import json
    json.dump({"verified": len(failures) == 0,
               "tests_run": tests_run,
               "tests_passed": tests_passed},
              open("verdict.json", "w"))
