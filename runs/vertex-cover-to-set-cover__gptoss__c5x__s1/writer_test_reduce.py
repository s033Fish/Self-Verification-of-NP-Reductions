import itertools
import random
import json
from problems import VertexCover, SetCover
from reduce import reduce

def vertex_cover_bruteforce(inst):
    n = inst['n']
    edges = inst['edges']
    k = inst['k']
    if k < 0:
        return False
    # enumerate subsets up to size k
    for r in range(min(k, n) + 1):
        for subset in itertools.combinations(range(n), r):
            covered = True
            for u, v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False

def set_cover_bruteforce(inst):
    u = inst['universe_size']
    sets = inst['sets']
    k = inst['k']
    if k < 0:
        return False
    if u == 0:
        return True
    # check each element appears in at least one set
    all_elements = set(range(u))
    for elem in all_elements:
        if not any(elem in s for s in sets):
            return False
    m = len(sets)
    for r in range(min(k, m) + 1):
        for combo in itertools.combinations(range(m), r):
            covered = set()
            for idx in combo:
                covered.update(sets[idx])
            if covered == all_elements:
                return True
    return False

def generate_random_vertex_cover_instance(max_n=5, max_edges=6):
    n = random.randint(0, max_n)
    possible_edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = random.sample(possible_edges, k=random.randint(0, min(len(possible_edges), max_edges)))
    k = random.randint(-1, n+1)
    return {'n': n, 'edges': [list(e) for e in edges], 'k': k}

def main():
    random.seed(0)
    tests = 200
    passed = 0
    for _ in range(tests):
        inst = generate_random_vertex_cover_instance()
        # validate source
        VertexCover.validate(inst)
        vc_ans = vertex_cover_bruteforce(inst)
        red = reduce(inst)
        SetCover.validate(red)
        sc_ans = set_cover_bruteforce(red)
        if vc_ans == sc_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('Source:', inst)
            print('Reduced:', red)
            print('vc_ans', vc_ans, 'sc_ans', sc_ans)
            break
    print(f'Passed {passed}/{tests}')
    # write verdict
    verdict = {
        'verified': passed == tests,
        'tests_run': tests,
        'tests_passed': passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
