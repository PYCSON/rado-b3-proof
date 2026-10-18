import sys,json;sys.path.insert(0,sys.argv[1]);import azbfun as Z
cnf,side,K1=sys.argv[2],sys.argv[3],int(sys.argv[4])
J=json.load(open(side));rho=J['rho'];V=J['vertices'];NV=3*len(V)
cls=[list(map(int,l.split()))[:-1] for l in open(cnf) if l.strip() and l[0] not in 'cp']
base=[c for c in cls if all(abs(v)<=NV for v in c)]
viol=0;tot=0
for k in range(J['kmin'],K1+1):
    a=3*k+rho;N,col=Z.colouring(a,3)
    val=[col[3*(p[0]*k*k+p[1]*k+p[2])] if kind=='h' else col[1+a*(p[0]*k*k+p[1]*k+p[2])] for kind,p in V]
    true=lambda v:(val[(abs(v)-1)//3]==(abs(v)-1)%3)==(v>0)
    for c in base:
        tot+=1
        if not any(true(v) for v in c): viol+=1
print(side.split('/')[-1],'k',J['kmin'],'..',K1,'clause evaluations',tot,'violated by AZB colouring',viol)
