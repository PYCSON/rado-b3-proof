# One CNF per rho: pure polynomial window (prefix h(1..8) FREE, 3 colours) AND
#   [ prefix uses 3 colours  OR  h(3)!=h(6)  OR  prefix is one of the 11 hard prefixes under some colour renaming ].
# UNSAT  =>  every solution-free colouring has h(1..8) two-coloured, h(3)=h(6), and not hard  (=> the third-colour lemma and E4 apply).
import sys,itertools;sys.path.insert(0,sys.argv[1]);import winpref as T
HARD=['AAAAAAAA','AAAAAAAB','AAAAAABA','AAAABAAA','AAAABABA','AAABAAAA','ABAAAAAA','ABBBABAB','ABBBABBB','ABBBBBAB','ABBBBBBB']
def free_cnf(W,rho,heads,hard=HARD,use3=True,useneq=True):
    k0=max(5,(2*W)//3+1)
    F,H,ab,bb,seeds=T.build(W,rho,k0,heads=heads,prefix='AAAAAAAA')   # seeds only used to include h(1..8) as vertices
    keys=[('h',x) for x in H]+[('f',x) for x in F];idx={x:i for i,x in enumerate(keys)}
    var=lambda x,c:3*idx[x]+c+1;cl=[]
    for x in keys:
        cl.append([var(x,c) for c in range(3)]);cl+=[[-var(x,c),-var(x,d)] for c in range(3) for d in range(c+1,3)]
    for p,q,h in ab:
        for c in range(3): cl.append([-var(('h',h),c),-var(('f',p),c),-var(('f',q),c)])
    for x,s,t in bb:
        for c in range(3): cl.append(sorted({-var(('h',x),c),-var(('h',s),c),-var(('h',t),c)}))
    hv=lambda i,c:var(('h',(0,0,i)),c)
    nxt=[3*len(keys)];new=lambda:(nxt.__setitem__(0,nxt[0]+1),nxt[0])[1]
    big=[];aux={}
    if use3:
        d3=new();big.append(d3);aux['d3']=d3
        for c in range(3): cl.append([-d3]+[hv(i,c) for i in range(1,9)])
    if useneq:
        dn=new();big.append(dn);aux['dneq']=dn;es=[]
        for c in range(3):
            e=new();es.append(e);cl+=[[-e,hv(3,c)],[-e,-hv(6,c)]]
        cl.append([-dn]+es)
    for P in hard:
        for pi in itertools.permutations(range(3),2):
            m=new();big.append(m);aux[(P,pi)]=m
            for i,ch in enumerate(P,1): cl.append([-m,hv(i,pi['AB'.index(ch)])])
    cl.append(big)
    return cl,nxt[0],k0,aux
if __name__=='__main__':
    from pysat.solvers import Cadical153
    for W,hd in ((5,(1,2,'k','k1')),(7,(1,2,3,'k','k1')),(7,(1,2,3,'km1','k','k1','k2'))):
        for rho in (-2,-1):
            cl,nv,k0,_=free_cnf(W,rho,hd);s=Cadical153(bootstrap_with=cl);r=s.solve()
            msg='SAT' if r else 'UNSAT'
            if r:
                m=set(x for x in s.get_model() if x>0)
                pre=''.join('ABC'[[c for c in range(3) if 3*0+0 or True][0]] for _ in []) 
            print('W',W,'heads',hd,'rho',rho,'k0',k0,'vars',nv,'clauses',len(cl),msg,flush=True);s.delete()
