import random
from problems import SOURCE, TARGET
from reduce import reduce

def run():
    tests_run = 0
    tests_passed = 0

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        SOURCE.validate(inst)
        red = reduce(inst)
        TARGET.validate(red)
        a = SOURCE.is_yes(inst)
        b = TARGET.is_yes(red)
        if a == b:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "->", red, "src", a, "tgt", b)

    # Exhaustive small graphs (all graphs up to 6 vertices)
    for n in range(0, 7):
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        for mask in range(1 << len(pairs)):
            edges = [list(pairs[k]) for k in range(len(pairs)) if mask >> k & 1]
            check({"n": n, "edges": edges})

    # Random slightly larger
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 11)
        edges = []
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < 0.4:
                    edges.append([i, j])
        check({"n": n, "edges": edges})

    # Random instances via provided generator
    for _ in range(500):
        inst = SOURCE.random_instance(rng, rng.randint(0, 9))
        check(inst)

    print("tests_run", tests_run, "tests_passed", tests_passed)
    return tests_run, tests_passed

if __name__ == "__main__":
    run()
