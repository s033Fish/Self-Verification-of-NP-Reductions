import random
import sys

import problems
from reduce import reduce


def test_random_instances(num_trials=200, max_n=5, max_edges=7, max_k=5):
    rng = random.Random(0)
    passed = 0
    total = 0
    for _ in range(num_trials):
        # generate random graph
        n = rng.randint(0, max_n)
        possible_edges = [(u, v) for u in range(n) for v in range(u+1, n)]
        rng.shuffle(possible_edges)
        m = rng.randint(0, min(len(possible_edges), max_edges))
        edges = [list(possible_edges[i]) for i in range(m)]
        k = rng.randint(-2, max_k)  # include some negative ks
        src = {"n": n, "edges": edges, "k": k}
        # validate source
        try:
            problems.VertexCover.validate(src)
        except problems.InvalidInstance:
            continue  # skip invalid (should not happen)
        # compute answers
        src_yes = problems.VertexCover.is_yes(src)
        tgt = reduce(src)
        tgt_yes = problems.SetCover.is_yes(tgt)
        if src_yes != tgt_yes:
            print("Mismatch!", src, src_yes, tgt, tgt_yes, file=sys.stderr)
            return False, total+1
        passed += 1
        total += 1
    return True, total

if __name__ == "__main__":
    ok, count = test_random_instances()
    print(f"Tests run: {count}, passed: {ok}")
    sys.exit(0 if ok else 1)
