# Certify U(a) 3-colour UNSAT with LRAT (lrat-check + cake_lpr).  U(a)={3t:1<=t<=a^2+a+1} u {1+aq:0<=q<=a^2+a+7}, max = L=a^3+a^2+7a+1.
# Constraints: every ordered solution (x,y,z) in U^3 of a x + 3 y = 3 z is not monochromatic. Colour symmetry breaking:
# c(1)=A (vertex 1 = 1+a*0) and c(3) in {A,B} (WLOG by renaming colours).
import sys,os,subprocess,hashlib,time
T=sys.argv[1];ledger=sys.argv[2]
done=set(l.split(',')[0] for l in open(ledger)) if os.path.exists(ledger) else set()
for a in map(int,sys.argv[3:]):
    if str(a) in done: continue
    H=a*a+a+1;U=sorted(set([3*t for t in range(1,H+1)]+[1+a*q for q in range(0,a*a+a+8)]));S=set(U);idx={v:i for i,v in enumerate(U)}
    L=a**3+a*a+7*a+1;assert max(U)==L
    var=lambda v,c:3*idx[v]+c+1;cl=[]
    for v in U:
        cl.append([var(v,c) for c in range(3)]);cl+=[[-var(v,c),-var(v,d)] for c in range(3) for d in range(c+1,3)]
    ntri=0
    for x in U:
        for y in U:
            s=a*x+3*y
            if s%3==0 and s//3 in S:
                z=s//3;ntri+=1
                for c in range(3): cl.append(sorted({-var(x,c),-var(y,c),-var(z,c)}))
    cl.append([var(1,0)]);cl.append([var(3,0),var(3,1)])
    n=3*len(U);p=f'U{a}.cnf'
    with open(p,'w') as f:
        f.write(f'p cnf {n} {len(cl)}\n');[f.write(' '.join(map(str,c))+' 0\n') for c in cl]
    h=hashlib.sha256(open(p,'rb').read()).hexdigest()
    t=time.time();r=subprocess.run([T+'/cadical/build/cadical','-q','--lrat','--no-binary',p,p+'.lrat'],capture_output=True);ts=time.time()-t
    st={20:'UNSAT',10:'SAT'}.get(r.returncode,f'rc{r.returncode}')
    lc=ck='-'
    if st=='UNSAT':
        lc='VERIFIED' if 'c VERIFIED' in subprocess.run([T+'/drat-trim/lrat-check',p,p+'.lrat'],capture_output=True,text=True).stdout else 'FAIL'
        ck=subprocess.run([T+'/cake_lpr/cake_lpr','--CML_HEAP_SIZE=6000','--CML_STACK_SIZE=2000',p,p+'.lrat'],capture_output=True,text=True).stdout.strip().splitlines()[-1]
    sz=os.path.getsize(p+'.lrat') if os.path.exists(p+'.lrat') else 0
    open(ledger,'a').write(f'{a},{len(U)},{ntri},{n},{len(cl)},{h},{st},{lc},{ck},{ts:.1f},{sz}\n')
    for fn in (p+'.lrat',): 
        if os.path.exists(fn): os.remove(fn)
