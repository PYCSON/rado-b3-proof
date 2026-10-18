# Glue check: for every colouring of h(1..8) (3^8), decide whether the AUX part of the free CNF (aux clauses + big
# clause, with h(1..8) fixed) is satisfiable. Must hold:  satisfiable  <=>  normalized prefix NOT in the 53 admissible prefixes.
import sys,json,itertools
from pysat.solvers import Cadical153
cnf,side,adm=sys.argv[1],sys.argv[2],sys.argv[3]
J=json.load(open(side));V=J['vertices'];NV=3*len(V)
hidx={tuple(p):i for i,(k,p) in enumerate(V) if k=='h'}
cls=[list(map(int,l.split()))[:-1] for l in open(cnf) if l.strip() and l[0] not in 'cp']
auxcl=[c for c in cls if any(abs(v)>NV for v in c)]
ADM53=set(l.split()[0] for l in open(adm))
def norm(col):
    m={};s=''
    for c in col:
        if c not in m: m[c]='ABC'[len(m)]
        s+=m[c]
    return s
bad=0;nin=0
for col in itertools.product(range(3),repeat=8):
    units=[[3*hidx[(0,0,i+1)]+col[i]+1] for i in range(8)]+[[-(3*hidx[(0,0,i+1)]+c+1)] for i in range(8) for c in range(3) if c!=col[i]]
    s=Cadical153(bootstrap_with=auxcl+units);sat=s.solve();s.delete()
    p=norm(col);inset=p in ADM53;nin+=inset
    if sat==inset: bad+=1;print('MISMATCH',col,p,sat,inset)
print('colourings',3**8,'in 53-set',nin,'(expected 53*6=318)','mismatches',bad)
