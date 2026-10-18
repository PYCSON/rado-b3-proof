# Concrete integer audit (different method from audit_free.py): for each k, evaluate every vertex as an integer and
# check every non-aux 3/2-literal negative clause is a monochromatic-forbidding clause of a genuine solution of
# a*x+3y=3z inside [1, L-1] (x,y,z integers; vertices: h(t)->3t, f(q)->1+a*q).
import sys,json,itertools
cnf,side,K1=sys.argv[1],sys.argv[2],int(sys.argv[3])
J=json.load(open(side));rho=J['rho'];V=J['vertices'];NV=3*len(V)
cls=[list(map(int,l.split()))[:-1] for l in open(cnf) if l.strip() and l[0] not in 'cp']
neg=[c for c in cls if all(v<0 for v in c) and len(c)>=2 and all(abs(v)<=NV for v in c) and len({(abs(v)-1)%3 for v in c})==1 and len({(abs(v)-1)//3 for v in c})==len(c) and not (len(c)==2 and (abs(c[0])-1)//3==(abs(c[1])-1)//3)]
neg=[c for c in neg if not (len(c)==2 and len({(abs(v)-1)//3 for v in c})==1)]
bad=0;n=0
for k in range(J['kmin'],K1+1):
    a=3*k+rho;L1=a**3+a*a+7*a
    val=[(3*(p[0]*k*k+p[1]*k+p[2]) if kind=='h' else 1+a*(p[0]*k*k+p[1]*k+p[2])) for kind,p in V]
    for c in neg:
        xs=[val[(abs(v)-1)//3] for v in c]
        if len(xs)==2: cands=[(xs[0],xs[0],xs[1]),(xs[0],xs[1],xs[1]),(xs[1],xs[0],xs[0]),(xs[1],xs[1],xs[0]),(xs[0],xs[1],xs[0]),(xs[1],xs[0],xs[1])]
        else: cands=list(itertools.permutations(xs))
        ok=any(a*x+3*y==3*z and min(x,y,z)>=1 and max(x,y,z)<=L1 for x,y,z in cands)
        n+=1;bad+=not ok
print(side.split('/')[-1],'k',J['kmin'],'..',K1,'triple-clause instances',n,'bad',bad)
