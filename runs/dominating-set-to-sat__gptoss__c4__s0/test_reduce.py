import random, json, sys
from problems import DominatingSet, Sat
from reduce import reduce
from solve_bruteforce import dominating_set_bruteforce, sat_bruteforce

def random_instance(max_n=4, max_k=2):
    """Generate a tiny instance suitable for exhaustive SAT checking.
    The SAT reduction creates k*n variables, so we keep both n and k small.
    """
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = []
    for u, v in possible_edges:
        if random.random() < 0.4:
            edges.append([u, v])
    k = random.randint(-1, max(max_k, n + 1))
    return {"n": n, "edges": edges, "k": k}

def test_one():
    for _ in range(200):
        inst = random_instance()
        ds_ans = dominating_set_bruteforce(inst)
        sat_inst = reduce(inst)
        sat_ans = sat_bruteforce(sat_inst)
        if ds_ans != sat_ans:
            print('Mismatch!')
            print('Dom instance:', json.dumps(inst))
            print('Sat instance:', json.dumps(sat_inst))
            print('Dom ans', ds_ans, 'Sat ans', sat_ans)
            sys.exit(1)
    print('All tests passed')

if __name__ == '__main__':
    test_one()
