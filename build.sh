#!/usr/bin/env bash
set -e

(cd cdict/; dune build -p dfa,cdict,cdict-tool)
cdict_tool () { cdict/_build/install/default/bin/cdict-tool "$@"; }

FORMAT_VERSION=$(cdict_tool format-version)
OUT_DIR="v$FORMAT_VERSION"
mkdir -p "$OUT_DIR"

for wl in aosp-dictionaries/wordlists/main_fr.combined; do
  wl_name=${wl##*/main_}
  wl_name=${wl_name%%.*}
  out="$OUT_DIR/$wl_name.dict"
  echo "=> $out"
  if [[ -e $out ]]; then continue; fi
  cdict_tool build -o "$out" "$wl"
  gzip -9 -c "$out" > "$out.gz"
  mv "$out.gz" "$out"
done

mkdir -p gen
python gen_dict_list.py "$OUT_DIR" \
  > "gen/SupportedDictionaries.v$FORMAT_VERSION.java"
