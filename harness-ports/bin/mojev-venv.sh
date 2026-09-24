#!/bin/bash
# Build ~/venv-mojev for the MoJev Gate 0 probe (task #230): the same torch and transformers as ~/laya-venv
# (2.14.0+cpu, 5.17.0) plus pillow and the matching CPU torchvision. Additive: no existing venv is touched.
set -u
exec > "$HOME/mojev-venv.log" 2>&1
echo "start $(date -u +%H:%M:%SZ)"
PY=$(~/laya-venv/bin/python -c 'import sys; print(sys.executable)')
BASE=$(~/laya-venv/bin/python -c 'import sys; print(sys.base_prefix)')/bin/python3.11
[ -x "$BASE" ] || BASE=python3.11
"$BASE" -m venv "$HOME/venv-mojev" || { echo "FAIL venv"; exit 1; }
P="$HOME/venv-mojev/bin/pip"
"$P" install -q --upgrade pip || { echo "FAIL pip"; exit 1; }
"$P" install -q --index-url https://download.pytorch.org/whl/cpu torch==2.14.0 torchvision==0.29.0 || { echo "FAIL torch"; exit 1; }
"$P" install -q transformers==5.17.0 safetensors==0.8.0 tokenizers==0.23.2 "pillow>=11" "numpy>=1.26" "pyarrow>=14" || { echo "FAIL deps"; exit 1; }
"$HOME/venv-mojev/bin/python" -c 'import torch, torchvision, transformers, PIL; print("torch", torch.__version__, "torchvision", torchvision.__version__, "transformers", transformers.__version__, "pillow", PIL.__version__)'
"$HOME/venv-mojev/bin/pip" freeze > "$HOME/venv-mojev.freeze.txt"
echo "DONE $(date -u +%H:%M:%SZ)"
