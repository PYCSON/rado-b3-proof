#!/bin/bash
# Replay every certificate with both proof checkers.
# Usage: LRAT_CHECK=/path/to/lrat-check CAKE_LPR=/path/to/cake_lpr bash certificates/replay.sh
# Expected: small_a 16, lemma_W 2, third_colour_late 53, third_colour_early 53, lemma_W_alt 2 VERIFIED; 0 FAILED.
# Exit status: 0 only if all five directories pass; nonzero otherwise.
set -euo pipefail
cd "$(dirname "$0")"
status=0
for spec in small_a:16 lemma_W:2 third_colour_late:53 third_colour_early:53 lemma_W_alt:2; do
  p="${spec%:*}"
  required="${spec#*:}"
  shopt -s nullglob
  proofs=( "$p"/*.lrat.xz )
  shopt -u nullglob
  if [ "${#proofs[@]}" -ne "$required" ]; then
    echo "ERROR: $p has ${#proofs[@]} LRAT files, expected $required" >&2
    status=1
  fi
  bash replay_part.sh "$p" || status=1
done
if [ "$status" -ne 0 ]; then echo "REPLAY FAILED" >&2; exit 1; fi
echo "ALL 126 CERTIFICATES VERIFIED"
