# Polynomial window helpers: a = 3k+rho, rho in {-2,-1}, k = ceil(a/3).
# Formal window with a substituted: every f position c*a+3kD+e (c = c0 + c1*k) becomes a polynomial
# 3c1 k^2 + (3c0 + rho c1 + 3D) k + (rho c0 + e); identical polynomials denote the same integer (merged, sound).
# Constraints kept only when valid for every k >= k0.  (Optional seed constraints in cnf()/build() are not used by freecnf.py.)
import sys
from itertools import combinations
ROWS={0:((0,0),{0:(0,None),1:(None,None),2:(None,0)}),
      1:((0,1),{1:(-1,None),2:(None,None),3:(None,4)}),
      2:((1,1),{1:(-2,None),2:(None,None),3:(None,4)})}
def poly(c,D,e,rho): c0,c1=c; return (3*c1, 3*c0+rho*c1+3*D, rho*c0+e)
def ev(p,k): return p[0]*k*k+p[1]*k+p[2]
def pos_all(p,k0):   # p(k)>0 for all integers k>=k0
    a,b,c=p
    if a<0 or (a==0 and b<0): return False
    if a==0 and b==0: return c>0
    ks=[k0]
    if a>0:
        v=-b/(2*a)
        if v>k0: ks+=[int(v),int(v)+1]
    return all(ev(p,k)>0 for k in ks if k>=k0)
def sub(p,q): return tuple(x-y for x,y in zip(p,q))
def add(p,q): return tuple(x+y for x,y in zip(p,q))
def build(W,rho,k0,heads=(1,2,'k','k1'),seedset='pure8',useAB=True,useBB=True,prefix='AAAAAAAA'):
    F=[]
    for r,(lay,lm) in ROWS.items():
        for D,(lo,hi) in lm.items():
            for e in range(-W,W+1):
                if (lo is None or e>=lo) and (hi is None or e<=hi): F.append(poly(lay,D,e,rho))
    F=sorted(set(F))
    H=set();ab=[]
    for p,q in combinations(F,2):
        d=sub(q,p)
        if pos_all(d,k0): ab.append((p,q,d));H.add(d)
        elif pos_all(sub(p,q),k0): ab.append((q,p,sub(p,q)));H.add(sub(p,q))
    X={1:(0,0,3),2:(0,0,6),3:(0,0,9),'km1':(0,3,-3),'k':(0,3,0),'k1':(0,3,3),'k2':(0,3,6)}
    AU={1:(0,3,rho),2:(0,6,2*rho),3:(0,9,3*rho),'km1':(3,rho-3,-rho),'k':(3,rho,0),'k1':(3,3+rho,rho),'k2':(3,6+rho,2*rho)}
    X={u:X[u] for u in heads};AU={u:AU[u] for u in heads}
    seeds={(0,0,e):prefix[e-1] for e in range(1,len(prefix)+1)}
    if seedset=='old':
        seeds[(0,0,9)]='A';seeds.update({(0,3,-3):'A',(0,3,-6):'A',(0,3,-9):'A',(0,3,0):'B'})
    H|=set(X.values())|set(seeds)
    bb=[]
    for s in list(H):
        if not pos_all(s,k0): continue
        for u in AU:
            t=add(s,AU[u])
            if t in H: bb.append((X[u],s,t))
    # sanity: every f value lies in [0, N] and every h value in [1, H] for k>=k0 (N=a^2+a+6, Hh=a^2+a+1)
    a=(0,3,rho);a2=(9,6*rho,rho*rho);Hh=add(add(a2,a),(0,0,1));N=add(add(a2,a),(0,0,6))
    for f in F: assert pos_all(add(f,(0,0,1)),k0) and pos_all(add(sub(N,f),(0,0,1)),k0)
    for h in H: assert pos_all(h,k0) and pos_all(add(sub(Hh,h),(0,0,1)),k0),h
    if not useAB: ab=[]
    if not useBB: bb=[]
    return F,sorted(H),ab,bb,seeds
def cnf(W,rho,k0,**kw):
    F,H,ab,bb,seeds=build(W,rho,k0,**kw)
    keys=[('h',x) for x in H]+[('f',x) for x in F];idx={x:i for i,x in enumerate(keys)}
    var=lambda x,c:3*idx[x]+c+1;cl=[]
    for x in keys:
        cl.append([var(x,c) for c in range(3)]);cl+=[[-var(x,c),-var(x,d)] for c in range(3) for d in range(c+1,3)]
    for p,q,h in ab:
        for c in range(3): cl.append([-var(('h',h),c),-var(('f',p),c),-var(('f',q),c)])
    for x,s,t in bb:
        for c in range(3): cl.append(sorted({-var(('h',x),c),-var(('h',s),c),-var(('h',t),c)}))
    for h,col in seeds.items(): cl.append([var(('h',h),'ABC'.index(col))])
    return cl,(len(F),len(H),len(ab),len(bb))
