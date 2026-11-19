import itertools
import sys
from problems import SOURCE as VertexCover, TARGET as Clique
from reduce import reduce

def brute_check(instance):
    return VertexCover.is_yes(instance)

def test_all_small():
    # enumerate small instances up to scale 4 (n up to 4, edges all combos, k range)
    count = 0
    for inst in VertexCover.enumerate_instances(scale=4):
        # Validate instance (should be already valid)
        VertexCover.validate(inst)
        expected = VertexCover.is_yes(inst)
        reduced = reduce(inst)
        Clique.validate(reduced)
        got = Clique.is_yes(reduced)
        if expected != got:
            print("Mismatch!", inst, "reduced", reduced, "expected", expected, "got", got, file=sys.stderr)
            assert False
        count += 1
    print("tested", count, "instances")

# Additional edge case tests
def test_edge_cases():
    # No edges, various k
    for n in range(0, 5):
        for k in range(-2, n+3):
            inst = {"n": n, "edges": [], "k": k}
            VertexCover.validate(inst)
            expected = VertexCover.is_yes(inst)
            reduced = reduce(inst)
            Clique.validate(reduced)
            got = Clique.is_yes(reduced)
            assert expected == got, (inst, reduced, expected, got)
    # Complete graph, check k extremes
    for n in range(1, 5):
        edges = [[u, v] for u in range(n) for v in range(u+1, n)]
        for k in range(-1, n+2):
            inst = {"n": n, "edges": edges, "k": k}
            VertexCover.validate(inst)
            expected = VertexCover.is_yes(inst)
            reduced = reduce(inst)
            Clique.validate(reduced)
            got = Clique.is_yes(reduced)
            assert expected == got, (inst, reduced, expected, got)

if __name__ == "__main__":
    test_all_small()
    test_edge_cases()
    print("All tests passed")
