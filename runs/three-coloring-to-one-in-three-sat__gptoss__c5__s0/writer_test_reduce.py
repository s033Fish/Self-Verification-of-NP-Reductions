import itertools
import json
import random
from problems import ThreeColoring, OneInThreeSat
from reduce import reduce

def three_coloring_bruteforce(instance):
    n = instance["n"]
    edges = instance["edges"]
    for colors in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colors[u] == colors[v]:
                ok = False
                break
        if ok:
            return True
    return False

def one_in_three_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assign in itertools.product([False, True], repeat=m):
        good = True
        for a, b, c in clauses:
            cnt = assign[a-1] + assign[b-1] + assign[c-1]
            if cnt != 1:
                good = False
                break
        if good:
            return True
    return False

def generate_all_graphs(n):
    vertices = list(range(n))
    edges = []
    all_possible = [(i, j) for i in range(n) for j in range(i+1, n)]
    for mask in range(1 << len(all_possible)):
        edges = [list(all_possible[i]) for i in range(len(all_possible)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def run_tests():
    total = 0
    passed = 0
    # test n up to 4 (exhaustive) and a few random for n=5
    for n in range(0, 5):
        for graph in generate_all_graphs(n):
            total += 1
            ThreeColoring.validate(graph)
            src_yes = three_coloring_bruteforce(graph)
            red = reduce(graph)
            OneInThreeSat.validate(red)
            tgt_yes = one_in_three_bruteforce(red)
            if src_yes == tgt_yes:
                passed += 1
            else:
                print("FAIL", graph, src_yes, red, tgt_yes)
    # random tests for n=5
    for _ in range(50):
        n = 5
        edges = []
        for i in range(n):
            for j in range(i+1, n):
                if random.random() < 0.3:
                    edges.append([i, j])
        graph = {"n": n, "edges": edges}
        total += 1
        ThreeColoring.validate(graph)
        src_yes = three_coloring_bruteforce(graph)
        red = reduce(graph)
        OneInThreeSat.validate(red)
        tgt_yes = one_in_three_bruteforce(red)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("FAIL random", graph, src_yes, red, tgt_yes)
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
