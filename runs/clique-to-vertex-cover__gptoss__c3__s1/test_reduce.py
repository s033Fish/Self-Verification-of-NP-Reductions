import random
from problems import Clique, VertexCover
from reduce import reduce

def test_random_instances():
    rng = random.Random(0)
    total = 0
    passed = 0
    for scale in range(1, 5):  # small scales
        for _ in range(20):
            inst = Clique.random_instance(rng, scale)
            # ensure valid
            Clique.validate(inst)
            reduced = reduce(inst)
            VertexCover.validate(reduced)
            # compare answers
            assert Clique.is_yes(inst) == VertexCover.is_yes(reduced)
            passed += 1
            total += 1
    print(f"Random tests passed: {passed}/{total}")

def test_edge_cases():
    # k <= 0
    inst = {"n": 5, "edges": [], "k": 0}
    reduced = reduce(inst)
    assert VertexCover.is_yes(reduced) == True
    # k > n
    inst = {"n": 3, "edges": [], "k": 5}
    reduced = reduce(inst)
    assert VertexCover.is_yes(reduced) == False
    # normal case
    inst = {"n": 4, "edges": [[0,1],[1,2],[2,3],[0,2]], "k": 3}
    reduced = reduce(inst)
    assert Clique.is_yes(inst) == VertexCover.is_yes(reduced)

if __name__ == "__main__":
    test_random_instances()
    test_edge_cases()
    print("All tests passed")
