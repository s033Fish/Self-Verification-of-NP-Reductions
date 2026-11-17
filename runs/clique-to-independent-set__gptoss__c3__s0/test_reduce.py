import random
from problems import Clique, IndependentSet
from reduce import reduce

def test_random_instances(num_trials=200):
    rng = random.Random(0)
    passed = 0
    for _ in range(num_trials):
        # generate small random instance with n up to 5
        n = rng.randint(0,5)
        # random edges
        edges = []
        for u in range(n):
            for v in range(u+1,n):
                if rng.random() < 0.5:
                    edges.append([u,v])
        k = rng.randint(-1, n+2)  # include edge cases
        inst = {"n": n, "edges": edges, "k": k}
        # validate
        Clique.validate(inst)
        # reduce
        red = reduce(inst)
        IndependentSet.validate(red)
        # compare answers
        if Clique.is_yes(inst) == IndependentSet.is_yes(red):
            passed += 1
        else:
            print("Mismatch!", inst, red, Clique.is_yes(inst), IndependentSet.is_yes(red))
            return False, passed
    return True, passed

if __name__ == "__main__":
    ok, passed = test_random_instances()
    total = 200
    print(f"Passed {passed}/{total}: {ok}")
