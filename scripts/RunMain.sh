#!/usr/bin/env bash
# Runs main.py for one model on one dataset and saves each run to results/<model>/<csv>.<target>.<time>.txt
# e.g. scripts/RunMain.sh jev 01 (a dataset with several targets, like 10, saves one file per target)
# extra arguments go to main.py, e.g. scripts/RunMain.sh gemini-flash 03 --samples 5

cd "$(dirname "$0")/.." || exit 1
source .venv/bin/activate

if [ $# -lt 2 ]; then
  echo "usage: scripts/RunMain.sh <model> <dataset number> [main.py arguments]"
  exit 1
fi
model=$1
number=$2
shift 2

models=$(python3 -c "from mappers.models import MODELS; print(*MODELS)")
if [[ " $models " != *" $model "* ]]; then
  echo "unknown model $model, pick one of: $models"
  exit 1
fi

# each expected file is named <csv>.<target>.json, which says which CSV and target to use
expected_files=(expected/"$number"_*.json)
if [ ! -e "${expected_files[0]}" ]; then
  echo "no expected files for dataset $number"
  exit 1
fi

mkdir -p "results/$model"
time=$(date +%Y-%m-%d_%H-%M-%S)

for path in "${expected_files[@]}"; do
  file_name=$(basename "$path" .json)
  name=${file_name%%.*}
  target_name=${file_name#*.}
  out="results/$model/$name.$target_name.$time.txt"

  {
    echo "model    = $model"
    echo "csv      = data/$name.csv"
    echo "target   = targets/$target_name.json"
    echo "expected = $path"
    echo "time     = $time"
    echo "args     = $*"
    echo
  } | tee "$out"

  python3 main.py "data/$name.csv" --target "targets/$target_name.json" --expected "$path" --model "$model" "$@" 2>&1 | tee -a "$out"

  # main.py prints one OK or x line per input
  right=$(grep -c '^OK ' "$out")
  total=$(grep -cE '^(OK|x ) ' "$out")
  if [ "$total" -gt 0 ]; then
    { echo; echo "right    = $right/$total"; } | tee -a "$out"
  fi
  echo "saved $out"
  echo
done
