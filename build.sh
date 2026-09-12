#!/usr/bin/env bash
set -e

(cd cdict/; dune build -p dfa,cdict,cdict-tool)
cdict_tool () { cdict/_build/install/default/bin/cdict-tool "$@"; }

FORMAT_VERSION=$(cdict_tool format-version)
OUT_DIR="v$FORMAT_VERSION"
mkdir -p "$OUT_DIR" "gen/v$FORMAT_VERSION"

declare -A wordlists=()

add()
{
  for wl in "$@"; do
    wl_name=${wl##*/main_}
    wl_name=${wl_name%%.*}
    wordlists[$wl_name]="$wl"
  done
}

remove()
{
  for wl in "$@"; do
    unset 'wordlists[$wl]'
  done
}

# Add experimental wordlists
add aosp-dictionaries/wordlists_experimental/main_*.combined
# Add stable wordlists last so they take precedence
add aosp-dictionaries/wordlists/main_*.combined

# Language codes that are not supported by the Babel library
remove mwl tcy bn2 el2 tr2 pms

i=0
for wl_name in "${!wordlists[@]}"; do
  i=$((i+1))
  wl="${wordlists[$wl_name]}"
  out="$OUT_DIR/$wl_name.dict"
  printf "[%02d/%d] => %s\n" "$i" "${#wordlists[@]}" "$out"
  if [[ -e $out ]]; then echo "(cached)"; continue; fi
  extra_args=()
  emoji_dict="aosp-dictionaries/wordlists/emoji_$wl_name.combined"
  if [[ -e $emoji_dict ]]; then
    extra_args+=("emoji:$emoji_dict")
  else
    # For example, the emoji wordlist for "en_GB" is "emoji_en"
    emoji_dict="aosp-dictionaries/wordlists/emoji_${wl_name%_*}.combined"
    if [[ -e $emoji_dict ]]; then
      extra_args+=("emoji:$emoji_dict")
    fi
  fi
  cdict_tool build --subst-file=substitutions.json -o "$out" "main:$wl" "${extra_args[@]}"
  gzip -9 -n -c "$out" > "$out.gz"
  mv "$out.gz" "$out"
done

(cd v1; sha256sum *.dict > checksums.txt)

python gen_dict_list.py "$OUT_DIR"
