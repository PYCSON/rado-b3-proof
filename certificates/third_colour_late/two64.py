# a-independent certificates for the 64 -> 11 two-colour prefix reduction (a>=23 with E4).
# For a normalized prefix X in {A,B}^8 (X[0]=A, X[2]=X[5]) let C be the unused colour.  Claim: no C in h(9..m0).
#  (i)  CNF_I(X,K,F): h(1..8)=X, some h(t)=C with 9<=t<=K-1, all AB constraints not(h(t)=f(q)=f(q+t)) for q+t<=F.
#  (ii) CNF_R(X,K):   two f-rows of length K (f(0..K-1), f(t0..t0+K-1), t0>=K so disjoint), shared h(9..K-1) in {A,B},
#       row-internal AB for every step d<=K-1, and no column with both rows C (h(t0)=C).
# UNSAT of both => (for t0<=m0 and F, t0+K-1 inside the f range) C never appears in [9,m0].
import sys,itertools
from pysat.solvers import Cadical153
def cnf_I(X,K,F):
    nv=[0]
    def new(): nv[0]+=1;return nv[0]
    h={t:[new() for _ in range(3)] for t in range(1,F+1)};f={q:[new() for _ in range(3)] for q in range(0,F+1)}
    cl=[]
    for v in list(h.values())+list(f.values()): cl.append(v[:]);cl+=[[-v[i],-v[j]] for i in range(3) for j in range(i+1,3)]
    for t in range(1,9): cl.append([h[t]['ABC'.index(X[t-1])]])
    cl.append([h[t][2] for t in range(9,K)])
    for t in range(1,F+1):
        for q in range(0,F+1-t):
            for c in range(3): cl.append([-h[t][c],-f[q][c],-f[q+t][c]])
    return cl
def cnf_R(X,K):
    nv=[0]
    def new(): nv[0]+=1;return nv[0]
    hb={t:new() for t in range(9,K)}          # true = B, false = A  (h(9..K-1) in {A,B})
    rows=[[ [new() for _ in range(3)] for _ in range(K)] for _ in range(2)]
    cl=[]
    for R in rows:
        for v in R: cl.append(v[:]);cl+=[[-v[i],-v[j]] for i in range(3) for j in range(i+1,3)]
    for R in rows:
        for d in range(1,K):
            for i in range(K-d):
                if d<=8:
                    c='ABC'.index(X[d-1]);cl.append([-R[i][c],-R[i+d][c]])
                else:
                    cl.append([hb[d],-R[i][0],-R[i+d][0]]);cl.append([-hb[d],-R[i][1],-R[i+d][1]])
    for i in range(K): cl.append([-rows[0][i][2],-rows[1][i][2]])
    return cl
def sat(cl):
    s=Cadical153(bootstrap_with=cl);r=s.solve();s.delete();return r
PATS=['A'+''.join(p) for p in itertools.product('AB',repeat=7)]
PATS=[p for p in PATS if p[2]==p[5]]
if __name__=='__main__':
    Kmax=int(sys.argv[1]);Fextra=int(sys.argv[2])
    for X in PATS:
        Kr=None
        for K in range(10,Kmax+1):
            if not sat(cnf_R(X,K)): Kr=K;break
        if Kr is None: print(X,'row test SAT up to',Kmax,flush=True);continue
        I=sat(cnf_I(X,Kr,Kr-1+Fextra))
        print(X,'K',Kr,'CNF_I(F=%d)'%(Kr-1+Fextra),'SAT' if I else 'UNSAT',flush=True)
