# The three-colour Rado numbers of ax + 3y = 3z

**Theorem.** For every integer `a ≥ 4` with `3 ∤ a`,

    R_3(ax + 3y = 3z) = a^3 + a^2 + 7a + 1.

`R_3(E)` is the least `N` such that every 3-colouring of `{1, …, N}` contains a monochromatic solution of `E`
(the solution need not consist of distinct integers).

This is the case `b = 3` of Conjecture 1.1 of T. Ahmed, L. Zaman and C. Bright, *Symbolic Sets for Proving Bounds
on Rado Numbers* (SC² 2025; arXiv:2505.12085). The lower bound is their Theorem 1.3. This repository contains a
proof of the upper bound.

**Status:** computer-assisted proof candidate. Internally checked; not peer reviewed.

## Contents

| Path | Content |
|---|---|
| `proof/proof.pdf` (`proof.tex`) | The complete proof |
| `certificates/` | 126 propositional formulas (DIMACS) with LRAT unsatisfiability proofs; generators and audit scripts |
| `tools/check_hand_proofs.py` | Mechanical check of every explicit triple and range condition in the hand-proved parts |
| `SHA256SUMS` | SHA-256 of every file |

## Outline of the proof

Write `H = a²+a+1`, `L = a³+a²+7a+1`, `h(t) = c(3t)` and `f(q) = c(1+aq)`. Every solution has `x = 3w`, and only
three families of solutions are used (see Section 2 of the proof).

1. `4 ≤ a ≤ 26`: one unsatisfiable formula per value of `a` (16 certificates).
2. `a ≥ 13`, Lemma W: writing `a = 3k+ρ` with `k = ⌈a/3⌉`, a fixed system of constraints whose positions are
   integer polynomials in `k` shows that the colours of `3, 6, …, 24` form one of 53 patterns (2 certificates).
3. `a ≥ 23`: for each of these patterns the third colour cannot appear early (106 certificates, independent of
   `a`), and an elementary chain argument then forces the pattern `AABAABAA`.
4. `a ≥ 7`, no computer: from `AABAABAA` the colours of all multiples of 3 up to `3H` are determined, and `L`
   admits no colour.

## Verifying

### Proof checkers

| Tool | Repository | Commit |
|---|---|---|
| lrat-check | https://github.com/marijnheule/drat-trim | `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` |
| cake_lpr (formally verified) | https://github.com/tanyongkiam/cake_lpr | `a36874a8b750b43fe4b385b8ddbf5b033e46a3fa` |
| CaDiCaL (only to regenerate proofs) | https://github.com/arminbiere/cadical | `c60730422e758ef1cebe7aeddf2dda31c996bf04` |

```bash
git clone https://github.com/marijnheule/drat-trim && (cd drat-trim && git checkout 2e3b2dc && make lrat-check)
git clone https://github.com/tanyongkiam/cake_lpr && (cd cake_lpr && git checkout a36874a && make cake_lpr)
```

### Steps

The commands are for Bash (Linux, macOS, or WSL on Windows; not native PowerShell). Requirements: `bash`, `xz`,
`sha256sum`, Python 3, and for step 3 the package `python-sat` (`python3 -m pip install python-sat`; tested
with python-sat 1.9.dev15). Run every command below from the repository root, in order. Set the two checker paths
first:

```bash
export LRAT_CHECK=/path/to/drat-trim/lrat-check
export CAKE_LPR=/path/to/cake_lpr/cake_lpr
```

1. Integrity of every file:

```bash
sha256sum -c SHA256SUMS
```

2. Replay all 126 certificates with both checkers (expected: `VERIFIED 16 / 2 / 53 / 53 / 2`, `FAILED 0`):

```bash
bash certificates/replay.sh
```

For each certificate the script checks the SHA-256 of the formula against the directory's `CNF_SHA256.txt`, then
requires `c VERIFIED` from `lrat-check` and `s VERIFIED UNSAT` from `cake_lpr`. It prints
`ALL 126 CERTIFICATES VERIFIED` and exits with status 0 only if every certificate passes; otherwise it exits with a
nonzero status.

3. Audits of the Lemma W formulas (Python 3; `glue.py` and `blkcheck2.py` need `python-sat`):

```bash
(cd certificates/lemma_W && \
 python3 audit/audit_free.py free_W7_rho-2.cnf free_W7_rho-2.coords.json && \
 python3 audit/audit_free.py free_W7_rho-1.cnf free_W7_rho-1.coords.json && \
 python3 audit/concrete_free.py free_W7_rho-2.cnf free_W7_rho-2.coords.json 60 && \
 python3 audit/concrete_free.py free_W7_rho-1.cnf free_W7_rho-1.coords.json 60 && \
 python3 audit/glue.py free_W7_rho-2.cnf free_W7_rho-2.coords.json audit/admissible_prefixes.txt && \
 python3 audit/glue.py free_W7_rho-1.cnf free_W7_rho-1.coords.json audit/admissible_prefixes.txt && \
 python3 ../lemma_W_alt/blkcheck2.py ../lemma_W_alt/gpt_block_rho-2.cnf free_W7_rho-2.coords.json free_W7_rho-2.cnf audit/admissible_prefixes.txt && \
 python3 ../lemma_W_alt/blkcheck2.py ../lemma_W_alt/gpt_block_rho-1.cnf free_W7_rho-1.coords.json free_W7_rho-1.cnf audit/admissible_prefixes.txt)
```

Expected: `ALL CLAUSES GENUINE FOR ALL k>= 5` (twice), `bad 0` (twice), `mismatches 0` (twice), and
`set equal: True` with `... admissible colourings: True` (twice). `audit/admissible_prefixes.txt` lists the 53
admissible patterns. `audit_free.py` checks every clause of a formula for all integers `k >= 5`; `concrete_free.py`
checks the (AB)/(BB) clauses only, on integers, for `k = 5..60`.

4. Hand-proved parts (standard library only; expected last line: `... 0 with errors`):

```bash
python3 tools/check_hand_proofs.py 400
```

### Regenerating the formulas

All 124 formulas used in the proof are reproduced byte-for-byte by the included generators:
`certificates/small_a/ucert.py` (U(a)), `certificates/lemma_W/generator/mkfree.py` (Lemma W),
`certificates/third_colour_*/two64.py` (third-colour lemma).

## Use of AI tools

The proof strategy, the computer encodings, the checking scripts and the text were developed with substantial
assistance from AI systems (Anthropic Claude and OpenAI GPT), which also cross-checked one another's computations
independently. All unsatisfiability claims rest on the certificates and independent proof checkers above.

## Verification record

On 18 October 2026 all 126 certificates were replayed from a clean copy of this repository with the checker
commits above (`VERIFIED 16 / 2 / 53 / 53 / 2`, `FAILED 0`), the Lemma W audits passed, the 124 formulas used in the
proof were regenerated byte-for-byte, and `tools/check_hand_proofs.py 400` reported no errors.

## Author

Puyi Sun (GitHub: PYCSON)

## License

See `LICENSE`.
