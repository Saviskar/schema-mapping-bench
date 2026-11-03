#!/usr/bin/env bash
# Runs eval.py on every dataset for every model at the same time, one log per model in results/
# Extra arguments go to eval.py, e.g. scripts/RunAllModels.sh --detail --seed 1

cd "$(dirname "$0")/.." || exit 1
source .venv/bin/activate

mkdir -p results
rm -f results/*.txt

for m in $(python3 -c "from mappers.models import MODELS; print(*MODELS)"); do
  python3 eval.py --model "$m" "$@" > "results/$m.txt" 2>&1 &
done
wait

# the total line of each model
tail -n 1 results/*.txt
