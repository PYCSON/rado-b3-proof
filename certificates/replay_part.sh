#!/bin/bash
# Usage: LRAT_CHECK=/path/lrat-check CAKE_LPR=/path/cake_lpr bash replay_part.sh <directory>
# For every <name>.lrat.xz in the directory: obtain <name>.cnf (plain or .xz), check its SHA-256 against
# CNF_SHA256.txt, then run lrat-check (must print "c VERIFIED") and cake_lpr (must print "s VERIFIED UNSAT").
# Exit status: 0 only if every certificate in the directory passed (and there was at least one); 1 otherwise.
set -u -o pipefail
if [ $# -ne 1 ] || [ ! -d "$1" ]; then echo "usage: replay_part.sh <directory>" >&2; exit 2; fi
for v in LRAT_CHECK CAKE_LPR; do
  p="${!v:-}"
  if [ -z "$p" ] || [ ! -x "$p" ]; then echo "error: $v must point to an executable (got '${p}')" >&2; exit 2; fi
done
D=$(cd "$1" && pwd); W=$(mktemp -d); ok=0; bad=0; expected=0
trap 'rm -rf "$W"' EXIT
if [ ! -f "$D/CNF_SHA256.txt" ]; then
  echo "error: missing CNF_SHA256.txt in $D" >&2
  exit 1
fi
# Every listed formula must have its own LRAT proof. Do not silently skip missing proofs.
while IFS= read -r record || [ -n "$record" ]; do
  [ -z "$record" ] && continue
  expected=$((expected+1))
  if [[ "$record" =~ ^[0-9a-f]{64}[[:space:]][[:space:]]([A-Za-z0-9._-]+)\.cnf$ ]]; then
    name="${BASH_REMATCH[1]}"
    if [ ! -f "$D/$name.lrat.xz" ]; then
      echo "FAIL missing LRAT for $name.cnf"
      bad=$((bad+1))
    fi
  else
    echo "FAIL malformed CNF_SHA256.txt entry"
    bad=$((bad+1))
  fi
done < "$D/CNF_SHA256.txt"
for L in "$D"/*.lrat.xz; do
  [ -e "$L" ] || continue
  n=$(basename "$L" .lrat.xz)
  if [ -f "$D/$n.cnf" ]; then cp "$D/$n.cnf" "$W/$n.cnf"; prep=$?
  else xz -dc "$D/$n.cnf.xz" > "$W/$n.cnf"; prep=$?; fi
  xz -dc "$L" > "$W/$n.lrat"; prep2=$?
  want=$(grep "  $n.cnf\$" "$D/CNF_SHA256.txt" | cut -d' ' -f1)
  got=$(sha256sum < "$W/$n.cnf" | cut -d' ' -f1)
  a=$("$LRAT_CHECK" "$W/$n.cnf" "$W/$n.lrat" | grep -cx 'c VERIFIED')
  a_rc=$?
  b=$("$CAKE_LPR" --CML_HEAP_SIZE=6000 --CML_STACK_SIZE=2000 "$W/$n.cnf" "$W/$n.lrat" | tail -1)
  b_rc=$?
  if [ "$prep" = 0 ] && [ "$prep2" = 0 ] && [ -n "$want" ] && [ "$want" = "$got" ] && [ "$a_rc" = 0 ] && [ "$b_rc" = 0 ] && [ "$a" = 1 ] && [ "$b" = "s VERIFIED UNSAT" ]; then
    ok=$((ok+1))
  else
    bad=$((bad+1))
    echo "FAIL $n unpack=$prep/$prep2 hash=$([ -n "$want" ] && [ "$want" = "$got" ] && echo ok || echo MISMATCH) lrat-check=$a cake_lpr=$b"
  fi
  rm -f "$W/$n.cnf" "$W/$n.lrat"
done
if [ "$expected" -eq 0 ] || [ $((ok+bad)) -ne "$expected" ]; then
  echo "ERROR: expected $expected proof(s) from CNF ledger, verified $ok" >&2
  bad=$((bad+1))
fi
echo "PART $(basename "$D"): VERIFIED $ok  FAILED $bad"
if [ "$bad" -gt 0 ] || [ "$ok" -eq 0 ]; then exit 1; fi
exit 0
