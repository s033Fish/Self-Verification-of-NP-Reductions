import itertools
import json
from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce

def is_hamiltonian_path(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
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

def is_hamiltonian_cycle(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n < 3:
        return False
    # cycle must start and end same, so consider permutations of vertices
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n):
            u = perm[i]
            v = perm[(i+1)%n]
            if frozenset((u, v)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def generate_all_instances(max_n=5):
    instances = []
    for n in range(max_n+1):
        verts = list(range(n))
        possible_edges = [(u, v) for u in verts for v in verts if u < v]
        for mask in range(1 << len(possible_edges)):
            edges = []
            for i, (u, v) in enumerate(possible_edges):
                if mask & (1 << i):
                    edges.append([u, v])
            instances.append({"n": n, "edges": edges})
    return instances

if __name__ == "__main__":
    instances = generate_all_instances(5)
    total = len(instances)
    passed = 0
    for inst in instances:
        # validate source (should be valid by construction)
        HamiltonianPath.validate(inst)
        src_ans = is_hamiltonian_path(inst)
        red = reduce(inst)
        # validate target
        HamiltonianCycle.validate(red)
        tgt_ans = is_hamiltonian_cycle(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", inst, src_ans, red, tgt_ans)
            break
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))
