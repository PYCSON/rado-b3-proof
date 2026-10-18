# Write the final free-prefix CNFs + coordinate sidecar (vertex polynomials, aux meaning).
import sys,json,hashlib;sys.path.insert(0,sys.argv[1]);import freecnf as FC, winpref as T
from pysat.solvers import Cadical153
W=int(sys.argv[2]);HD=(1,2,'k','k1')
for rho in (-2,-1):
    cl,nv,k0,aux=FC.free_cnf(W,rho,HD);s=Cadical153(bootstrap_with=cl);r=s.solve();s.delete()
    print('W',W,'rho',rho,'k0',k0,'vars',nv,'clauses',len(cl),'SAT' if r else 'UNSAT',flush=True)
    if r or len(sys.argv)<4: continue
    F,H,ab,bb,_=T.build(W,rho,k0,heads=HD,prefix='AAAAAAAA')
    keys=[['h',list(x)] for x in H]+[['f',list(x)] for x in F]
    name=f'free_W{W}_rho{rho}'
    body=''.join(' '.join(map(str,c))+' 0\n' for c in cl)
    txt=f'c pure polynomial window, prefix free, a=3k{rho:+d}, k>={k0}; vertex i (0-based) colour c -> var 3i+c+1; aux vars > {3*len(keys)}\np cnf {nv} {len(cl)}\n'+body
    open(name+'.cnf','w').write(txt)
    json.dump({'rho':rho,'kmin':k0,'W':W,'heads':[str(x) for x in HD],'vertices':keys,
               'aux':{(k if isinstance(k,str) else f'{k[0]}|{k[1][0]}{k[1][1]}'):v for k,v in aux.items()},
               'aux_semantics':{'d3':'-> each colour c occurs among h(1..8)','dneq':'-> some e_c: h(3)=c and h(6)!=c (e_c = dneq+1+c)',
                                'P|xy':'-> h(i) = colour x if P[i]==A else colour y, i=1..8'}},open(name+'.coords.json','w'))
    print(name,hashlib.sha256(txt.encode()).hexdigest())
