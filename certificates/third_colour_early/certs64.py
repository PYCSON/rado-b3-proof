import sys,os,subprocess,hashlib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import two64
T=sys.argv[1];os.makedirs('cnf',exist_ok=True)
rows=[l.split() for l in open('two64.out') if ' K ' in l]
def cert(name,cl):
    n=max(abs(l) for c in cl for l in c);p=f'cnf/{name}.cnf'
    with open(p,'w') as f:
        f.write(f'p cnf {n} {len(cl)}\n');[f.write(' '.join(map(str,c))+' 0\n') for c in cl]
    r=subprocess.run([T+'/cadical/build/cadical','-q','--lrat','--no-binary',p,p+'.lrat'],capture_output=True)
    a=subprocess.run([T+'/drat-trim/lrat-check',p,p+'.lrat'],capture_output=True,text=True).stdout
    b=subprocess.run([T+'/cake_lpr/cake_lpr','--CML_HEAP_SIZE=4000','--CML_STACK_SIZE=2000',p,p+'.lrat'],capture_output=True,text=True).stdout.strip().splitlines()[-1]
    subprocess.run(['gzip','-f','-9',p+'.lrat'])
    print(name,n,len(cl),hashlib.sha256(open(p,'rb').read()).hexdigest(),'rc',r.returncode,'lrat-check','VERIFIED' if 'c VERIFIED' in a else 'FAIL','cake_lpr',b,flush=True)
for r in rows:
    X=r[0];K=int(r[2]);F=K-1+80
    cert(f'R_{X}_K{K}',two64.cnf_R(X,K))
    cert(f'I_{X}_K{K}_F{F}',two64.cnf_I(X,K,F))
