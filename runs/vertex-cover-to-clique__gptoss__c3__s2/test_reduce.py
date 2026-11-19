import random
from problems import SOURCE, TARGET
from reduce import reduce

def test_random_instances(num_trials=200):
    rng = random.Random(0)
    for _ in range(num_trials):
        # scale determines size; use small scale like 4
        inst = SOURCE.random_instance(rng, scale=4)
        reduced = reduce(inst)
        assert SOURCE.is_yes(inst) == TARGET.is_yes(reduced), f"Mismatch on {inst} -> {reduced}"

def test_edge_cases():
    # k < 0
    inst = {"n": 3, "edges": [[0,1],[1,2]], "k": -1}
    reduced = reduce(inst)
    assert not SOURCE.is_yes(inst)
    assert not TARGET.is_yes(reduced)

    # k >= n
    inst = {"n": 3, "edges": [[0,1]], "k": 3}
    reduced = reduce(inst)
    assert SOURCE.is_yes(inst)
    assert TARGET.is_yes(reduced)

    # empty graph
    inst = {"n": 4, "edges": [], "k": 2}
    reduced = reduce(inst)
    assert SOURCE.is_yes(inst)  # empty graph always yes for k>=0
    assert TARGET.is_yes(reduced)  # complement is complete, clique size n-k=2

if __name__ == "__main__":
    test_random_instances()
    test_edge_cases()
    print("All tests passed")
