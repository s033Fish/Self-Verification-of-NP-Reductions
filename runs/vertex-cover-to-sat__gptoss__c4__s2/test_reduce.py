import itertools, random, json, sys
from problems import VertexCover, Sat
import reduce

def solve_vc(inst):
    n=inst['n']; edges=inst['edges']; k=inst['k']
    if k<0: return False
    if not edges: return True
    if k>=n: return True
    for r in range(k+1):
        for subset in itertools.combinations(range(n), r):
            s=set(subset)
            if all(u in s or v in s for u,v in edges):
                return True
    return False

def solve_sat(inst):
    m=inst['num_vars']; clauses=inst['clauses']
    for clause in clauses:
        if not clause:
            return False
    for bits in itertools.product([False,True], repeat=m):
        ok=True
        for clause in clauses:
            if not any((lit>0 and bits[abs(lit)-1]) or (lit<0 and not bits[abs(lit)-1]) for lit in clause):
                ok=False; break
        if ok:
            return True
    return False

random.seed(0)
total=0; passed=0
for _ in range(200):
    n=random.randint(0,5)  # keep n small for brute force
    edges=[]
    for u in range(n):
        for v in range(u+1,n):
            if random.random()<0.5:
                edges.append([u,v])
    # limit k to small values to keep variable count low
    k=random.randint(-1, min(n,3))
    src={'n':n,'edges':edges,'k':k}
    VertexCover.validate(src)
    sat=reduce.reduce(src)
    Sat.validate(sat)
    if solve_vc(src)==solve_sat(sat):
        passed+=1
    else:
        print('Mismatch',src)
        sys.exit(1)
    total+=1
verdict={'verified': True, 'tests_run': total, 'tests_passed': passed}
with open('verdict.json','w') as f:
    json.dump(verdict,f)
print('All tests passed',passed,'/',total)
