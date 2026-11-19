import random
from problems import IndependentSet, Clique
from reduce import reduce

def run_tests(num_trials=200, max_n=6):
    rng = random.Random(0)
    passed = 0
    total = 0
    for _ in range(num_trials):
        n = rng.randint(0, max_n)
        # generate random edge set
        possible = [(u, v) for u in range(n) for v in range(u+1, n)]
        edges = []
        for (u, v) in possible:
            if rng.random() < 0.5:
                edges.append([u, v])
        k = rng.randint(-2, n+2)  # include values outside range
        instance = {"n": n, "edges": edges, "k": k}
        # validate via IndependentSet.validate (may raise)
        try:
            IndependentSet.validate(instance)
        except Exception as e:
            # shouldn't happen because we generated valid format
            print("Invalid generated instance", e)
            continue
        yes_ind = IndependentSet.is_yes(instance)
        reduced = reduce(instance)
        # ensure reduced is valid Clique instance
        Clique.validate(reduced)
        yes_clique = Clique.is_yes(reduced)
        total += 1
        if yes_ind == yes_clique:
            passed += 1
        else:
            print("Mismatch!", instance, reduced, yes_ind, yes_clique)
            break
    return passed, total

if __name__ == "__main__":
    passed, total = run_tests()
    print(f"Tests passed: {passed}/{total}")
