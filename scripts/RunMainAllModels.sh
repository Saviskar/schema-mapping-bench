#!/usr/bin/env bash
# Runs main.py with every model, one model after another
# No dataset number runs every dataset in a row; a number runs just that one, e.g. scripts/RunMainAllModels.sh 01
# (a dataset with several targets, like 10, runs each one; extra arguments go to main.py, e.g. --samples 5)

cd "$(dirname "$0")/.." || exit 1
source .venv/bin/activate

# each expected file is named <csv>.<target>.json, which says which CSV and target to use
if [ $# -eq 0 ] || [[ $1 == -* ]]; then
  expected_files=(expected/*.json)
else
  number=$1
  shift
  expected_files=(expected/"$number"_*.json)
  if [ ! -e "${expected_files[0]}" ]; then
    echo "no expected files for dataset $number"
    exit 1
  fi
fi

models=$(python3 -c "from mappers.models import MODELS; print(*MODELS)")

for path in "${expected_files[@]}"; do
  file_name=$(basename "$path" .json)
  name=${file_name%%.*}
  target_name=${file_name#*.}
  echo "##### $name -> $target_name"
  for m in $models; do
    echo "== $m"
    python3 main.py "data/$name.csv" --target "targets/$target_name.json" --expected "$path" --model "$m" "$@"
    echo
  done
done
