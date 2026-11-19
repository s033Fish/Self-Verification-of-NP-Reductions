import itertools
import json
import sys
from problems import ThreeColoring, IndependentSet
from reduce import reduce

def three_colorable(instance):
    n = instance['n']
    edges = instance['edges']
    # try all assignments of 0,1,2
    for colors in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colors[u] == colors[v]:
                ok = False
                break
        if ok:
            return True
    return False

def independent_set_at_least(instance):
    n = instance['n']
    edges_set = {frozenset(e) for e in instance['edges']}
    k = instance['k']
    # generate subsets of size >= k
    vertices = list(range(n))
    for r in range(k, n+1):
        for subset in itertools.combinations(vertices, r):
            # check independent
            independent = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges_set:
                    independent = False
                    break
            if independent:
                return True
    return False

def generate_all_instances(max_n=4):
    instances = []
    for n in range(max_n+1):
        # all possible edges without duplicates, undirected
        all_pairs = [(i, j) for i in range(n) for j in range(i+1, n)]
        for r in range(len(all_pairs)+1):
            for edges in itertools.combinations(all_pairs, r):
                # convert to list of lists
                edges_list = [list(e) for e in edges]
                instance = {'n': n, 'edges': edges_list}
                instances.append(instance)
    return instances

def main():
    instances = generate_all_instances(4)
    total = len(instances)
    passed = 0
    for inst in instances:
        # validate source
        ThreeColoring.validate(inst)
        src_ans = three_colorable(inst)
        red = reduce(inst)
        IndependentSet.validate(red)
        tgt_ans = independent_set_at_least(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('source', inst)
            print('src_ans', src_ans)
            print('reduced', red)
            print('tgt_ans', tgt_ans)
            sys.exit(1)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('All tests passed', passed, '/', total)

if __name__ == '__main__':
    main()
