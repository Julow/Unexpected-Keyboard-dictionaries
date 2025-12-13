#!/usr/bin/env bash
set -e

(cd cdict/; dune build -p dfa,cdict,cdict-tool)
cdict_tool () { cdict/_build/install/default/bin/cdict-tool "$@"; }

FORMAT_VERSION=$(cdict_tool format-version)
OUT_DIR="v$FORMAT_VERSION"
mkdir -p "$OUT_DIR" "gen/v$FORMAT_VERSION"

# Wordlists that are ignored because they do not have a corresponding entry in
# locale_config.xml
declare -A disabled=(
  [eo]=1
  [gom]=1
  [he]=1
  [hi_ZZ]=1
  [ks]=1
  [la]=1
  [mwl]=1
  [sr_ZZ]=1
  [tcy]=1
  [tok]=1
  [zgh_ZZ]=1
)

for wl in aosp-dictionaries/wordlists/main_*.combined; do
  wl_name=${wl##*/main_}
  wl_name=${wl_name%%.*}
  if [[ ${disabled[$wl_name]} = 1 ]]; then continue; fi
  out="$OUT_DIR/$wl_name.dict"
  echo "=> $out"
  if [[ -e $out ]]; then echo "(cached)"; continue; fi
  cdict_tool build -o "$out" "main:$wl"
  gzip -9 -c "$out" > "$out.gz"
  mv "$out.gz" "$out"
done

python gen_dict_list.py "$OUT_DIR"
