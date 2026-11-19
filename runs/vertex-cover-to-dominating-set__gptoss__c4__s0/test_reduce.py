import itertools
import random
import json
from problems import VertexCover, DominatingSet
from reduce import reduce

def vc_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k < 0:
        return False
    # edge cases handled by brute force anyway
    for r in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), r):
            S = set(subset)
            ok = True
            for u, v in edges:
                if u not in S and v not in S:
                    ok = False
                    break
            if ok:
                return True
    return False

def ds_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k < 0:
        return False
    # build adjacency list
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for r in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), r):
            D = set(subset)
            dominated = set(D)
            for v in D:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False

def random_instance(max_n=5, max_edges=7):
    n = random.randint(0, max_n)
    possible = [(i, j) for i in range(n) for j in range(i+1, n)]
    random.shuffle(possible)
    m = random.randint(0, min(len(possible), max_edges))
    edges = [list(e) for e in possible[:m]]
    k = random.randint(-1, n+1)
    return {"n": n, "edges": edges, "k": k}

def test_one():
    inst = random_instance()
    VertexCover.validate(inst)
    reduced = reduce(inst)
    DominatingSet.validate(reduced)
    ans_src = vc_bruteforce(inst)
    ans_tgt = ds_bruteforce(reduced)
    if ans_src != ans_tgt:
        print('Mismatch!')
        print('src', json.dumps(inst))
        print('reduced', json.dumps(reduced))
        print('src ans', ans_src, 'tgt ans', ans_tgt)
        return False
    return True

if __name__ == '__main__':
    trials = 200
    passed = 0
    for i in range(trials):
        if test_one():
            passed += 1
    print(f'Passed {passed}/{trials} trials')
    # write verdict
    verdict = {
        "verified": passed == trials,
        "tests_run": trials,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
