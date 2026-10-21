#!/usr/bin/env bash
# Optionally generate grasp-grid data (in parallel shards), then train the grasp MLP.
#
# Examples:
#   ./run_training.sh --generate 2000 --shards 8          # generate 2000 samples on 8 processes, then train
#   ./run_training.sh --lr 3e-4 --batch-size 64           # train on the existing dataset/
#   ./run_training.sh --generate 500 --no-train           # only generate
#   ./run_training.sh -- --num_workers 0                  # anything after -- goes to train_precision_mlp.py
#
# Environment (override by exporting before running):
#   PYTHON     python interpreter              (default: python3)
#   MUJOCO_GL  headless rendering backend      (default: egl; use osmesa without a GPU)
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: run_training.sh [options] [-- extra train_precision_mlp.py args]

Data generation (skipped unless --generate is given):
  --generate N         samples to generate before training
  --shards K           parallel generator processes (default 1)
  --start-idx I        index of the first sample (default 0)

Training (defaults are train_precision_mlp.py's):
  --epochs N           --patience N        --batch-size N
  --lr X               --weight-decay X    --hidden-dim N
  --dropout X          --val-frac X        --num-workers N
  --seed N             --device auto|cuda|mps|cpu
  --no-train           stop after data generation

Paths (relative to robotics/simulation/):
  --data-dir DIR       dataset root with images/ and labels/ (default dataset)
  --models-dir DIR     checkpoint directory (default models)
EOF
}

# Always run from robotics/simulation/, wherever the script is called from
SIM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SIM_DIR"

PYTHON="${PYTHON:-python3}"
export MUJOCO_GL="${MUJOCO_GL:-egl}"
# generate_data.py imports `simulation.*`, so robotics/ must be importable
export PYTHONPATH="$(cd .. && pwd)${PYTHONPATH:+:$PYTHONPATH}"
# Keep each generator process to one thread so parallel shards don't oversubscribe the CPU
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"

GENERATE=0
SHARDS=1
START_IDX=0
DATA_DIR=dataset
MODELS_DIR=models
DO_TRAIN=1
TRAIN_ARGS=()

need_value() { [[ $# -ge 2 && -n "$2" ]] || { echo "error: $1 needs a value" >&2; exit 2; }; }

while [[ $# -gt 0 ]]; do
    case "$1" in
        --generate)     need_value "$@"; GENERATE="$2"; shift 2 ;;
        --shards)       need_value "$@"; SHARDS="$2"; shift 2 ;;
        --start-idx)    need_value "$@"; START_IDX="$2"; shift 2 ;;
        --data-dir)     need_value "$@"; DATA_DIR="$2"; shift 2 ;;
        --models-dir)   need_value "$@"; MODELS_DIR="$2"; shift 2 ;;
        --no-train)     DO_TRAIN=0; shift ;;
        --epochs|--patience|--batch-size|--lr|--weight-decay|--hidden-dim|--dropout|--val-frac|--num-workers|--seed|--device)
            need_value "$@"
            TRAIN_ARGS+=("--$(echo "${1#--}" | tr '-' '_')" "$2"); shift 2 ;;
        -h|--help)      usage; exit 0 ;;
        --)             shift; TRAIN_ARGS+=("$@"); break ;;
        *)              echo "error: unknown option $1" >&2; usage >&2; exit 2 ;;
    esac
done

echo "MUJOCO_GL=$MUJOCO_GL  PYTHONPATH=$PYTHONPATH  PYTHON=$PYTHON"

# ---- Data generation ----
if [[ "$GENERATE" -gt 0 ]]; then
    mkdir -p "$DATA_DIR/logs"
    PER_SHARD=$(( (GENERATE + SHARDS - 1) / SHARDS ))
    PIDS=()
    echo "Generating $GENERATE samples in $SHARDS shard(s) into $DATA_DIR/ (logs in $DATA_DIR/logs/)"
    for (( k = 0; k < SHARDS; k++ )); do
        SHARD_START=$(( START_IDX + k * PER_SHARD ))
        REMAINING=$(( START_IDX + GENERATE - SHARD_START ))
        (( REMAINING <= 0 )) && break
        N=$(( REMAINING < PER_SHARD ? REMAINING : PER_SHARD ))
        # Each shard seeds NumPy from its start index, so shards differ and are reproducible
        "$PYTHON" generate_data.py --n_samples "$N" --start_idx "$SHARD_START" --output_dir "$DATA_DIR" \
            > "$DATA_DIR/logs/gen_${SHARD_START}.log" 2>&1 &
        PIDS+=($!)
        echo "  shard $k: samples $SHARD_START-$(( SHARD_START + N - 1 )) (pid $!)"
    done

    FAILED=0
    for pid in "${PIDS[@]}"; do
        wait "$pid" || FAILED=$(( FAILED + 1 ))
    done
    if (( FAILED > 0 )); then
        echo "error: $FAILED generator shard(s) failed -- see $DATA_DIR/logs/" >&2
        exit 1
    fi
    echo "Generation done: $(ls "$DATA_DIR/labels" | wc -l | tr -d ' ') label files in $DATA_DIR/labels/"
fi

# ---- Training ----
if (( DO_TRAIN )); then
    if [[ ! -d "$DATA_DIR/labels" ]]; then
        echo "error: $DATA_DIR/labels not found -- generate data first (--generate N)" >&2
        exit 1
    fi
    echo "Training: $PYTHON train_precision_mlp.py --labels_dir $DATA_DIR/labels --models_dir $MODELS_DIR ${TRAIN_ARGS[*]:-}"
    "$PYTHON" train_precision_mlp.py --labels_dir "$DATA_DIR/labels" --models_dir "$MODELS_DIR" "${TRAIN_ARGS[@]+"${TRAIN_ARGS[@]}"}"
fi
