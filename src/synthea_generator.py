"""
synthea_generator.py

This script runs the Synthea synthetic health record generator.  It uses
the command‑line interface to generate a small cohort of synthetic
patients for demonstration.  All data are written to the local
``data`` directory so no information leaves the workstation, in line
with organisational policies restricting external storage of PHI.
"""

import argparse
import os
import subprocess
import sys


def run_synthea(population: int) -> int:
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    cmd = [
        'synthea',
        '--exporter.baseDirectory', os.path.abspath(data_dir),
        '--population', str(population),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
        else:
            print(f"Generated {population} synthetic patients in {data_dir}")
        return result.returncode
    except FileNotFoundError:
        print(
            "Synthea executable not found. Please install Synthea (Java jar) and ensure it is on the PATH.",
            file=sys.stderr,
        )
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic patient data using Synthea.")
    parser.add_argument('--population', type=int, default=100, help='Number of patients to generate')
    args = parser.parse_args(argv)
    return run_synthea(args.population)


if __name__ == '__main__':
    sys.exit(main())