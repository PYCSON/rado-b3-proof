# Exact all-parameter audit of a free-prefix pure-window CNF. Reads ONLY the DIMACS file and its JSON sidecar.
# Does not import any generator.  Polynomials are triples (c2,c1,c0) meaning c2*k^2+c1*k+c0, k integer >= kmin.
# a = 3k+rho, H = a^2+a+1 (h-range [1,H]), F = H+5 (f-range [0,F]); L-1 = a^3+a^2+7a.
# Every clause must be one of:
#   ALO  (x_A or x_B or x_C) for one vertex;  AMO (-x_c or -x_d) for one vertex;
#   AB   (-h(t)_c, -f(p)_c, -f(q)_c) with q-p == t identically and t>=1, p>=0, q<=F for all k>=kmin
#        -> original solution (3t, 1+a p, 1+a q):  a*3t + 3(1+ap) = 3(1+aq);
#   BB   (-h(x)_c, -h(s)_c, -h(t)_c) with x = 3u, u in {constant>=1} or {k+j}, t-s == a*u identically,
#        s>=1, t<=H for all k>=kmin  -> original solution (3x, 3s, 3t): a*3x+9s = 9t  <=>  t = s + a*u;
#   AUX  clauses exactly as described in the sidecar (checked structurally below).
# No unit clauses are allowed (prefix is free).
import sys,json,hashlib,itertools
cnf,side=sys.argv[1],sys.argv[2]
raw=open(cnf,'rb').read();print('sha256',hashlib.sha256(raw).hexdigest())
J=json.load(open(side));rho=J['rho'];K0=J['kmin'];V=[(k,tuple(p)) for k,p in J['vertices']];NV=3*len(V)
cls=[];hdr=None
for ln in raw.decode().split('\n'):
    if not ln.strip() or ln[0]=='c': continue
    if ln[0]=='p': hdr=ln.split();continue
    x=list(map(int,ln.split()));assert x[-1]==0;cls.append(x[:-1])
assert int(hdr[3])==len(cls)
def sub(p,q): return tuple(a-b for a,b in zip(p,q))
def mul_a(u):  # (3k+rho)*u, u = (0,u1,u0)
    assert u[0]==0; return (3*u[1], 3*u[2]+rho*u[1], rho*u[2])
A=(0,3,rho); H=(9,6*rho+3,rho*rho+rho+1); F=(H[0],H[1],H[2]+5)
def nonneg(p):  # p(k)>=0 for every integer k>=K0, exact
    c2,c1,c0=p; f=lambda k:c2*k*k+c1*k+c0
    if c2<0 or (c2==0 and c1<0): return False
    pts={K0}
    if c2>0:
        v=-c1//(2*c2)            # floor of vertex (exact integer arithmetic)
        pts|={v,v+1}
    return all(f(k)>=0 for k in pts if k>=K0)
def ge(p,c): return nonneg((p[0],p[1],p[2]-c))
def le(p,q): return nonneg(sub(q,p))
dec=lambda v:(V[(abs(v)-1)//3],(abs(v)-1)%3) if abs(v)<=NV else (('aux',abs(v)),None)
# Range of every vertex
for kind,p in V:
    assert (kind=='h' and ge(p,1) and le(p,H)) or (kind=='f' and ge(p,0) and le(p,F)),(kind,p)
cnt={'ALO':0,'AMO':0,'AB':0,'BB':0,'AUX':0,'BAD':0}
aux=J['aux'];auxv=set(aux.values())
d3=aux.get('d3');dn=aux.get('dneq')
hidx={p:i for i,(k,p) in enumerate(V) if k=='h'}
hv=lambda i,c:3*hidx[(0,0,i)]+c+1
expected_aux=[]
if d3: expected_aux+=[sorted([-d3]+[hv(i,c) for i in range(1,9)]) for c in range(3)]
if dn:
    es=[dn+1+c for c in range(3)]
    for c in range(3): expected_aux+=[sorted([-es[c],hv(3,c)]),sorted([-es[c],-hv(6,c)])]
    expected_aux.append(sorted([-dn]+es))
for key,m in aux.items():
    if '|' in key:
        P,xy=key.split('|');x,y=int(xy[0]),int(xy[1]);assert x!=y
        for i,ch in enumerate(P,1): expected_aux.append(sorted([-m,hv(i,x if ch=='A' else y)]))
expected_aux.append(sorted(aux.values()))
EA={}
for c in expected_aux: EA[tuple(c)]=EA.get(tuple(c),0)+1
for c in cls:
    if any(abs(v)>NV for v in c):
        t=tuple(sorted(c))
        if EA.get(t,0)>0: EA[t]-=1;cnt['AUX']+=1
        else: cnt['BAD']+=1;print('bad aux',c)
        continue
    D=[dec(v) for v in c]
    if len(c)==3 and all(v>0 for v in c) and len({d[0] for d in D})==1 and {d[1] for d in D}=={0,1,2}: cnt['ALO']+=1;continue
    if len(c)==2 and all(v<0 for v in c) and D[0][0]==D[1][0] and D[0][1]!=D[1][1]: cnt['AMO']+=1;continue
    ok=False
    if all(v<0 for v in c) and len({d[1] for d in D})==1 and len(c) in (2,3):
        hs=[d[0][1] for d in D if d[0][0]=='h'];fs=[d[0][1] for d in D if d[0][0]=='f']
        if len(hs)==1 and len(fs)==2:
            for p,q in itertools.permutations(fs):
                if sub(q,p)==hs[0] and ge(hs[0],1): ok=True;cnt['AB']+=1;break
        elif len(fs)==0:
            pts=hs if len(hs)==3 else None
            if pts is None and len(hs)==2:   # merged duplicate: x coincides with s or t
                pts=[hs[0],hs[0],hs[1]],[hs[0],hs[1],hs[1]],[hs[1],hs[0],hs[1]],[hs[1],hs[1],hs[0]]
                cand=[]
                for P in pts: cand+=list(itertools.permutations(P))
            else: cand=list(itertools.permutations(pts))
            for x,s,t in cand:
                if x[0]==0 and x[1]%3==0 and x[2]%3==0 and (x[1]//3 in (0,1)):
                    u=(0,x[1]//3,x[2]//3)
                    if (u[1]==0 and u[2]>=1) or (u[1]==1 and u[2]+K0>=1):
                        if sub(t,s)==mul_a(u) and ge(s,1) and le(t,H): ok=True;cnt['BB']+=1;break
    if not ok: cnt['BAD']+=1; print('BAD',c,D)
print(cnt,'unused expected aux',sum(EA.values()))
assert cnt['BAD']==0 and sum(EA.values())==0
print('ALL CLAUSES GENUINE FOR ALL k>=',K0)
