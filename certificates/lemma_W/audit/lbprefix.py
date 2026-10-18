# Consistency: the AZB solution-free colouring of [1,L-1] must have normalized prefix h(1..8)=c(3..24) in the 53-set
# (Lemma W + third-colour lemma) -- indeed it must be P0 -- and its h restricted to [1,H] must equal h* on [1,H-1] with h(H)=C (§4).
import sys;sys.path.insert(0,sys.argv[1]);import azbfun as Z
ADM53=set(open(sys.argv[2]).read().split())
for a in range(13,80):
    if a%3==0: continue
    N,col=Z.colouring(a,3)
    h=lambda t:col[3*t]
    m={};p=''
    for t in range(1,9):
        c=h(t)
        if c not in m: m[c]='ABC'[len(m)]
        p+=m[c]
    H=a*a+a+1
    hs=all((m.get(h(t)) if h(t) in m else 'C')==('B' if t%3==0 and t<=3*a else 'A') for t in range(1,H))
    hc=(h(H) not in m)
    print(a,p,'in53' if p in ADM53 else 'NOT-IN-53','P0' if p=='AABAABAA' else '','h=h* on [1,H-1]' if hs else 'h!=h*','h(H)=C' if hc else 'h(H)!=C')
