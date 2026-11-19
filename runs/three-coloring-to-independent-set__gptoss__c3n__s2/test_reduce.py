import itertools
import json
import random
import sys
from problems import ThreeColoring, IndependentSet
from reduce import reduce

def three_coloring_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    # assign colors 0,1,2
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False

def independent_set_bruteforce(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    # iterate subsets
    for r in range(k, n+1):
        for subset in itertools.combinations(range(n), r):
            # check independent
            good = True
            for i in range(len(subset)):
                for j in range(i+1, len(subset)):
                    if frozenset((subset[i], subset[j])) in edges:
                        good = False
                        break
                if not good:
                    break
            if good:
                return True
    return False


def generate_all_graphs(n):
    vertices = list(range(n))
    possible_edges = [(i, j) for i in vertices for j in vertices if i < j]
    for mask in range(1 << len(possible_edges)):
        edges = []
        for idx, (u, v) in enumerate(possible_edges):
            if mask & (1 << idx):
                edges.append([u, v])
        yield {'n': n, 'edges': edges}


def run_tests():
    total = 0
    passed = 0
    for n in range(0, 5):  # up to 4 vertices
        for graph in generate_all_graphs(n):
            # validate source
            ThreeColoring.validate(graph)
            src_yes = three_coloring_bruteforce(graph)
            reduced = reduce(graph)
            IndependentSet.validate(reduced)
            tgt_yes = independent_set_bruteforce(reduced)
            total += 1
            if src_yes == tgt_yes:
                passed += 1
            else:
                print('Mismatch', graph, src_yes, reduced, tgt_yes)
                sys.exit(1)
    # random larger tests
    for _ in range(100):
        n = random.randint(0, 6)
        # generate random edges
        edges = []
        for i in range(n):
            for j in range(i+1, n):
                if random.random() < 0.3:
                    edges.append([i, j])
        graph = {'n': n, 'edges': edges}
        ThreeColoring.validate(graph)
        src_yes = three_coloring_bruteforce(graph)
        reduced = reduce(graph)
        IndependentSet.validate(reduced)
        tgt_yes = independent_set_bruteforce(reduced)
        total += 1
        if src_yes == tgt_yes:
            passed += 1
        else:
            print('Mismatch random', graph, src_yes, reduced, tgt_yes)
            sys.exit(1)
    # write verdict
    verdict = {'verified': passed == total, 'tests_run': total, 'tests_passed': passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('All tests passed', total)

if __name__ == '__main__':
    run_tests()
