import itertools
import json
import sys
from problems import ThreeColoring, IndependentSet
from reduce import reduce

def three_coloring_solver(instance):
    n = instance['n']
    edges = instance['edges']
    # trivial cases
    if n == 0:
        return True
    if n <= 3:
        return True
    # check K4 quickly
    # not needed, brute force will handle
    for assignment in itertools.product(range(3), repeat=n):
        ok = True
        for u,v in edges:
            if assignment[u] == assignment[v]:
                ok = False
                break
        if ok:
            return True
    return False

def independent_set_solver(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # brute force subsets of size >=k
    vertices = list(range(n))
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            ok = True
            for u,v in itertools.combinations(subset,2):
                if frozenset((u,v)) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def generate_all_graphs(max_n):
    for n in range(max_n+1):
        verts = list(range(n))
        possible_edges = [(i,j) for i in verts for j in verts if i<j]
        for r in range(len(possible_edges)+1):
            for edges in itertools.combinations(possible_edges, r):
                yield {'n': n, 'edges': [list(e) for e in edges]}


def main():
    total = 0
    passed = 0
    for instance in generate_all_graphs(5):
        # validate source
        ThreeColoring.validate(instance)
        src_ans = three_coloring_solver(instance)
        red = reduce(instance)
        IndependentSet.validate(red)
        tgt_ans = independent_set_solver(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('source', instance)
            print('src_ans', src_ans)
            print('reduced', red)
            print('tgt_ans', tgt_ans)
            sys.exit(1)
        total += 1
    print('All tests passed', total)
    # write verdict
    import json
    with open('verdict.json','w') as f:
        json.dump({"verified": True, "tests_run": total, "tests_passed": passed}, f)

if __name__ == '__main__':
    main()
