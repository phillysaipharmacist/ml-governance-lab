    # ML Governance Lab

    This repository contains a **local-only** demonstration lab that trains
    a simple model on Synthea-generated data, evaluates it with
    Seismometer, monitors drift with Evidently and visualises metrics in
    Grafana.  All services bind to `127.0.0.1` so protected health
    information (PHI) never leaves the workstation, supporting privacy
    requirements to restrict access and storage to authorised devices.

    ## Prerequisites

    - **Docker Desktop ≥ 4.41.0**
    - **Python 3.11**
    - **Git**
    - **Administrator rights**

    ## Quickstart (Windows)

    1. Clone the repo and run `.\bootstrap\setup.ps1`.
    2. Generate secrets with `.\bootstrap\gen_secrets.sh`.
    3. `cd docker && docker compose up -d`.
    4. Install Python deps:
       ```
       python -m pip install --upgrade pip
       pip install pip-tools
       pip-compile --generate-hashes -o requirements.lock requirements.in
       pip install -r requirements.lock
       ```
    5. Launch UI: `python -m src.ui`.

    ## Quickstart (macOS/Linux)

    Similar steps using `./bootstrap/setup.sh` and Bash instead of PowerShell.

    ## Security & Compliance Notes

    - Local-only isolation (127.0.0.1 binding)
    - File-based Docker secrets
    - Deterministic, hashed dependencies
    - CI vulnerability scanning with Trivy

    ## Troubleshooting

    - Re-run `pip install -r requirements.lock` if packages missing.
    - Reset Grafana by deleting `docker/grafana_data`.

    ## License

    Educational purposes only. No PHI should be imported.