import sys,json
from collections import Counter
cnf,side,mine,adm=sys.argv[1:5]
J=json.load(open(side));V=[(k,tuple(p)) for k,p in J['vertices']];NV=3*len(V)
# alternative-encoding labels: (kind,(c0,c1,c2)) sorted; main-encoding labels (kind,(c2,c1,c0))
gl=sorted((k,(p[2],p[1],p[0])) for k,p in V)
gidx={t:i for i,t in enumerate(gl)}; myidx={(k,(p[2],p[1],p[0])):i for i,(k,p) in enumerate(V)}
remap=lambda x:(1 if x>0 else -1)*(3*myidx[gl[(abs(x)-1)//3]]+(abs(x)-1)%3+1)
rd=lambda f:[tuple(map(int,l.split()[:-1])) for l in open(f) if l.strip() and l[0] not in 'cp']
G=[tuple(sorted(remap(x) for x in c)) for c in rd(cnf)]
M=[tuple(sorted(set(c))) for c in rd(mine) if all(abs(x)<=NV for x in c)]
blk=[c for c in G if len(c)==8 and all(x<0 for x in c)];base=[c for c in G if c not in set(blk)]
print('base clauses: alternative',len(base),'main (dedup)',len(set(M)),'| set equal:',set(base)==set(M))
inv={3*myidx[('h',(i,0,0))]+c+1:(i,c) for i in range(1,9) for c in range(3)}
ADM53=set(open(adm).read().split())
norm=lambda col:(lambda m:''.join(m.setdefault(c,'ABC'[len(m)]) for c in col))({})
cols={tuple(dict(inv[-x] for x in c)[i] for i in range(1,9)) for c in blk}
print('blocked colourings',len(cols),'== all 318 admissible colourings:',len(cols)==318 and {norm(c) for c in cols}==ADM53 and all(norm(c) in ADM53 for c in cols))
