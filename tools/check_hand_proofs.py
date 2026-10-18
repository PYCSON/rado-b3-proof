"""Mechanical check of every explicit triple, index range and inequality used in the
hand-proved parts of the proof (sections 5 and 6 of proof.tex), for all a in a range.

Conventions (as in the proof):
  H = a^2+a+1, M = H-3, F = H+5, L = 1+a(H+6).
  BB triple <x, y, z> of h-indices: x = 3u (u>=1), y >= 1, z = y + a*u, all in [1, H].
    It corresponds to the solution (9u, 3y, 3z) of ax+3y=3z.
  AB triple (t; q, q+t): t in [1,H], q >= 0, q+t <= H+6; solution (3t, 1+aq, 1+a(q+t)).
  h* (t) = B iff t in {3,6,...,3a}, else A.
Run:  python3 check_hand_proofs.py [amax]      (standard library only)
"""
import sys
from math import ceil

def run(a):
    H = a*a + a + 1; M = H - 3; F = H + 5; L = 1 + a*(H + 6)
    assert L == a**3 + a*a + 7*a + 1
    Bset = set(range(3, 3*a + 1, 3))
    hs = lambda t: 'B' if t in Bset else 'A'
    errs = []
    def bb(x, y, z, lim=H, tag=''):
        ok = x % 3 == 0 and x >= 3 and y >= 1 and z == y + a*(x//3) and max(x, y, z) <= lim
        ok = ok and a*(3*x) + 3*(3*y) == 3*(3*z)          # genuine solution (9u,3y,3z)
        if not ok: errs.append(f'BB {tag} <{x},{y},{z}> lim {lim}')
    def need(cond, tag):
        if not cond: errs.append(tag)
    # numbers live in [1, L-1] for everything except the final step
    need(3*H <= L - 1 and 1 + a*F == L - a, 'ranges of h and f inside [1,L-1]')
    # ---- chain lemma (generic k): identities ----
    for k in range(2, a + 2):
        N = k*(a + 3)
        bb(3*k, 3*k, N, lim=10**18, tag='chain1'); bb(3*(k-1), 3*k + a, N, lim=10**18, tag='chain2')
        bb(3, N, N + a, lim=10**18, tag='chain3'); bb(3*k, 3*k + a, N + a, lim=10**18, tag='chain4')
    # ---- section 6 (a >= 7) ----
    if a >= 7:
        # U2C step 1: chain up to k = a-3 inside [1,M]
        need((a-3)*(a+3) + a <= M, 'U2C chain range')
        d, e, p, r, s, v, w, v3 = 3*(a-2), 3*(a-1), a+3, a*a-a+3, a*a+3, 2*a-6, a*a+a-6, a-6
        need(v3 >= 1, 'v3>=1')
        for x, y, z, t in [(3,3,p,'D1a'), (d,p,r,'D1b'), (3,r,s,'D1c'), (e,3,r,'D1d'), (e,p,s,'D1e'),
                           (3,v,d,'D2a'), (d,d,w,'D2b'), (e,v,w,'D2c'), (6,v3,d,'D3a'), (3*a,v3,w,'D3b')]:
            bb(x, y, z, lim=M, tag=t)
        # covering: every n in [1,M] \ Bset is the third entry of a BB triple whose other two entries are in Bset
        for n in range(1, M + 1):
            if n in Bset: continue
            u0 = next(u for u in (1, 2, 3) if (a*u - n) % 3 == 0)
            if n >= a*u0 + 3:
                found = False
                for u in range(u0, a + 1, 3):
                    vv = (n - a*u)
                    if vv % 3 == 0 and 1 <= vv//3 <= a:
                        bb(3*u, vv, n, lim=M, tag='cover'); found = True; break
                need(found, f'cover n={n}')
            else:
                need(u0 in (1, 2), f'cover small n={n} u0={u0}')
                if u0 == 1: bb(6, n, n + 2*a, lim=M, tag='cover6'); need(n + 2*a in Bset, f'cover6 B n={n}')
                if u0 == 2: bb(3, n, n + a, lim=M, tag='cover3'); need(n + a in Bset, f'cover3 B n={n}')
        # nine columns: rows f(0..8), f(t..t+8) inside [0,F] for t <= M
        need(M + 8 <= F, 'nine-column range')
        # tail lemma
        qT = 11 if a % 3 == 1 else 10
        need((1 + a*qT) % 3 == 0, 'qT'); sT = (1 + a*qT)//3
        need(3*a < sT <= M, 'sT range')
        bb(3*(a-2), 3*a, H-1, lim=H, tag='T H-1')
        if a % 3 == 1: bb(3*a, a-1, H-2, lim=H, tag='T H-2'); need(hs(3*a) == 'B' and hs(a-1) == 'B', 'T B1')
        else: bb(3*(a-1), 2*a-1, H-2, lim=H, tag='T H-2'); need(hs(3*(a-1)) == 'B' and hs(2*a-1) == 'B', 'T B2')
        need(hs(3*(a-2)) == 'B' and hs(3*a) == 'B', 'T H-1 B')
        for t in (H-2, H-1):
            need(t + 6 <= F, 'tail row range')
            for j in (0, 3, 6):
                dd = abs(qT - j); need(dd % 3 != 0 and 1 <= dd <= M and hs(dd) == 'A', f'tail upper {j}')
                dd = t + j - qT; need(3*a < dd <= M and hs(dd) == 'A', f'tail lower {t},{j}')
        # h(H) = C
        bb(3*a + 3, 1, H, lim=H, tag='HC A'); need(hs(3*a + 3) == 'A' and 3*a + 3 <= M, 'HC A colours')
        if a % 3 == 2: bb(3*a, a+1, H, lim=H, tag='HC B'); need(hs(a+1) == 'B', 'HC B2')
        else: bb(3*(a-1), 2*a+1, H, lim=H, tag='HC B'); need(hs(2*a+1) == 'B', 'HC B1')
        # final proposition
        q0 = 2 if a % 3 == 1 else 1
        need((1 + a*q0) % 3 == 0, 'q0')
        Q = [q0 + 3*j for j in range(a + 1)]
        col = {}
        for q in Q:
            s_ = (1 + a*q)//3; need(1 <= s_ <= M, f'Q s range {q}'); col[q] = hs(s_)
        need(sum(1 for q in Q if col[q] == 'B') == 1, 'exactly one B in Q')
        qB = [q for q in Q if col[q] == 'B'][0]; need(qB <= q0 + 6, 'B in Q has j<=2')
        plow = min(q for q in Q if col[q] == 'A'); need(plow <= 5, 'p_low<=5')
        phigh = q0 + 3*a; need(col[phigh] == 'A' and phigh <= F, 'p_high')
        need(3*a + 2 < H, 'step1 p_high<H')
        for q in range(H, H + 6):
            if (q - q0) % 3 == 0:
                dd = q - phigh; need(dd % 3 == 0 and 3*a < dd < H, f'step2 {q}')
        need(q0 % 3 != 0 and (3 - q0) % 3 != 0 and (6 - q0) % 3 != 0, 'positions 0,3,6 not = q0 mod 3')
        dd = H + 6 - phigh; need(dd == a*a - 2*a + 7 - q0 and 3*a < dd <= M and hs(dd) == 'A', 'final A')
    # ---- section 5 (a >= 23) ----
    if a >= 23:
        J = ceil((2*a + 8)/3); m0 = J*(a + 3) + a
        need((2*a + 8 + 2)//3 == J, 'J integer ceil')
        need(m0 <= H, 'm0<=H'); need(m0 + 67 <= F, 'third-colour late range m0+67<=F')
        need(147 <= F and 147 <= H, 'third-colour early range 147')
        for dlt in (1, 2, 4, 5, 7, 8):
            u = next(u for u in (1, 2) if (a*u + dlt) % 3 == 0); vv = (a*u + dlt)//3
            need(1 <= vv <= J, f'E4 v {dlt}'); bb(3*u, dlt, 3*vv, lim=m0, tag=f'E4 {dlt}')
    if a >= 13:
        k = ceil(a/3); rho = a - 3*k; need(rho in (-2, -1) and k >= 5, 'k,rho')
    return errs

if __name__ == '__main__':
    amax = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    bad = 0; n = 0
    for a in range(7, amax + 1):
        if a % 3 == 0: continue
        n += 1; e = run(a)
        if e: bad += 1; print(a, e[:5])
    print(f'checked {n} values of a in [7,{amax}] with 3 not dividing a: {bad} with errors')
