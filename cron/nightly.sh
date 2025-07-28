    #!/usr/bin/env bash
    # cron/nightly.sh

    set -euo pipefail

    run_step() {
        local name="$1"; shift
        echo "[cron] Starting $name…"
        if "$@"; then
            echo "[cron] $name completed."
        else
            echo "[cron] $name failed." >&2
        fi
    }

    SCRIPT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
    PY=python3.11

    run_step "preflight" $PY -m src.preflight
    run_step "synthea generation" $PY -m src.synthea_generator --population 200
    run_step "model training" $PY -m src.train_model
    run_step "seismometer evaluation" $PY -m src.evaluate_seismometer
    run_step "drift monitoring" $PY -m src.drift_monitor
    run_step "load results" $PY -m src.load_to_postgres

    echo "[cron] Nightly pipeline finished."