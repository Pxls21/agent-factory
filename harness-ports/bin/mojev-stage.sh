#!/bin/bash
# mojev-stage.sh: MoJev option B prep (task #210, D-069 item 3): clone the pinned code and download the pinned Hub files.
# Static only: nothing from either source is executed here. Every file is verified against the pin.
# Runs ON THE PC as the lane user. First run 2026-09-24 11:35:57Z-11:38:29Z (as ~/mojev-prep.sh, byte-identical below
# this header); its log is ~/mojev-prep.log. Re-running is safe: present files are re-verified, not re-fetched.
set -u
REV=0c8695b6252f4205907433d4e196a94f032e60c3
CODE=a74d58cd19ec573e83e8e27f9fecd837b8d830fb
SNAP="$HOME/mojev-snapshot/$REV"
exec >"$HOME/mojev-prep.log" 2>&1
echo "start $(date -u +%H:%M:%SZ)"
if [ ! -d "$HOME/mojev-pin/.git" ]; then
  GIT_LFS_SKIP_SMUDGE=1 git clone -q https://github.com/MoLeMo-Lab/mojev "$HOME/mojev-pin" || { echo "FAIL clone"; exit 1; }
fi
git -C "$HOME/mojev-pin" -c advice.detachedHead=false checkout -q "$CODE" || { echo "FAIL checkout"; exit 1; }
echo "code HEAD $(git -C "$HOME/mojev-pin" rev-parse HEAD)"
mkdir -p "$SNAP"
# name blob_or_empty lfs_sha256_or_empty size
while read -r name blob sha size; do
  out="$SNAP/$name"
  if [ ! -s "$out" ]; then
    curl -sSfL --retry 3 -o "$out.part" "https://huggingface.co/MoLeMo-Lab/mojev/resolve/$REV/$name" || { echo "FAIL download $name"; exit 1; }
    mv "$out.part" "$out"
  fi
  got_size=$(stat -c %s "$out")
  [ "$got_size" = "$size" ] || { echo "FAIL size $name $got_size != $size"; exit 1; }
  if [ "$sha" != "-" ]; then
    got=$(sha256sum "$out" | cut -d' ' -f1)
    [ "$got" = "$sha" ] && echo "OK sha256 $name $got" || { echo "FAIL sha256 $name $got"; exit 1; }
  else
    got=$(git hash-object "$out")
    case "$got" in "$blob"*) echo "OK blob $name $got";; *) echo "FAIL blob $name $got"; exit 1;; esac
  fi
done <<'LIST'
config.json 946557eb49d7 - 5935
modeling.py 8b1415ffb650 - 13390
schema.py cd99f6fdb8a4 - 7072
preprocessor_config.json 4e3fe0f26dc7 - 334
video_preprocessor_config.json 4d1c40497623 - 332
tokenizer_config.json d1a20cc3a883 - 1124
chat_template.jinja 0ef09f214eaa - 7755
README.md 56bb73fdbbb4 - 6724
tokenizer.json - 06b9509352d2af50381ab2247e083b80d32d5c0aba91c272ca9ff729b6a0e523 19989325
model.safetensors - eae27bf03e0e44501316cafab2406b1505732ddf4b836d19fbb8deb642f55f50 1710234304
LIST
echo "DONE $(date -u +%H:%M:%SZ)"
