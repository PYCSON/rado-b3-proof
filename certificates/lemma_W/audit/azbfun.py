# Check the AZB (arXiv 2505.12085v3, Thm 1.3 proof / Example 3.3) colouring of [1, a^3+a^2+(2b+1)a] for b=3:
# every element gets exactly one colour, and no monochromatic solution of a x + b y = b z (x,y,z in [1,N], not nec. distinct).
import sys
def colouring(a,b):
    N=a**3+a*a+(2*b+1)*a
    P=[(1,b*a),(b*a+1,b*b*a),(b*b*a+1,b*a*a+b*a),(b*a*a+b*a+1,a**3+a*a+(b+1)*a),(a**3+a*a+(b+1)*a+1,N)]
    col={}
    def put(n,c):
        assert n not in col,(n,col[n],c);col[n]=c
    for n in range(1,N+1):
        blk=[i for i,(lo,hi) in enumerate(P) if lo<=n<=hi][0]
        mb=(n%b==0);mb2=(n%(b*b)==0)
        if blk in (1,2) and not mb: put(n,0)
        if blk==3: put(n,0)
        if blk==0 and not mb: put(n,1)
        if blk in (0,1) and mb2: put(n,1)
        if blk==4: put(n,1)
        if blk in (0,1) and mb and not mb2: put(n,2)
        if blk==2 and mb: put(n,2)
    assert len(col)==N,(N,len(col))
    return N,col
def mono(a,b,N,col):
    bits=[0,0,0]
    for n,c in col.items(): bits[c]|=1<<n
    for x in range(b,N+1,b):          # gcd(a,b)=1 => x multiple of b; z = y + a x / b
        d=a*x//b
        if d>=N: break
        c=col[x];B=bits[c]
        if B & (B>>d) & ~1: return (x,d,c)
    return None
