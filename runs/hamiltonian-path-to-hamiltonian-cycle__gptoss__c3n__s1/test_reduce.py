import itertools
import json
from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce

def brute_hamiltonian_path(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    if n == 0:
        return False
    if n == 1:
        return True
    # generate all permutations of vertices
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n-1):
            if frozenset((perm[i], perm[i+1])) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def brute_hamiltonian_cycle(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    if n <= 2:
        return False
    # permutations of vertices fixing first to reduce symmetry
    for perm in itertools.permutations(range(n)):
        # need a cycle, so require edge between last and first
        ok = True
        for i in range(n):
            u = perm[i]
            v = perm[(i+1)%n]
            if frozenset((u,v)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def generate_all_instances(max_n=5):
    instances = []
    for n in range(max_n+1):
        vertices = list(range(n))
        possible_edges = [(u,v) for u in vertices for v in vertices if u < v]
        for mask in range(1 << len(possible_edges)):
            edges = []
            for i, e in enumerate(possible_edges):
                if mask & (1 << i):
                    edges.append([e[0], e[1]])
            instance = {'n': n, 'edges': edges}
            # validate
            try:
                HamiltonianPath.validate(instance)
                HamiltonianCycle.validate(instance)
            except Exception:
                # validation may fail for HamiltonianCycle when n<=2? but it's okay, they still validate.
                pass
            instances.append(instance)
    return instances


def main():
    instances = generate_all_instances(5)
    total = len(instances)
    passed = 0
    for inst in instances:
        # compute answers
        ans_path = brute_hamiltonian_path(inst)
        reduced = reduce(inst)
        ans_cycle = brute_hamiltonian_cycle(reduced)
        if ans_path == ans_cycle:
            passed += 1
        else:
            print('FAIL')
            print('orig', inst)
            print('reduced', reduced)
            print('path', ans_path, 'cycle', ans_cycle)
            break
    print(f'Ran {total} instances, passed {passed}')
    # write verdict
    verdict = {
        'verified': passed == total,
        'tests_run': total,
        'tests_passed': passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
