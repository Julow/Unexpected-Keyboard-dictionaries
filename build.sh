#!/usr/bin/env bash
set -e

(cd cdict/; dune build -p dfa,cdict,cdict-tool)
cdict_tool () { cdict/_build/install/default/bin/cdict-tool "$@"; }

OUT_DIR="v$(cdict_tool format-version)"
mkdir -p "$OUT_DIR"

for wl in aosp-dictionaries/wordlists/main_fr.combined; do
  wl_name=${wl##*/main_}
  wl_name=${wl_name%%.*}
  out="$OUT_DIR/$wl_name.dict"
  echo "=> $out"
  if [[ -e $out ]]; then continue; fi
  cdict_tool build -o "$out" "$wl"
done
