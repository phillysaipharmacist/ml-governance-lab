"""
drift_monitor.py

Simulate concept drift using Evidently.
"""
import json, os, sys

def run_drift_monitor() -> int:
        models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
        report_path = os.path.join(models_dir, 'drift.json')
        try:
            import pandas as pd, numpy as np
            from evidently import ColumnMapping
            from evidently.report import Report
            from evidently.metrics import DatasetDriftMetric
        except ImportError:
            print("Evidently is not installed; skipping drift simulation.", file=sys.stderr)
            return 1
        rng = np.random.default_rng(seed=0)
        ref = pd.DataFrame(rng.normal(size=(200,5)), columns=[f"f{i}" for i in range(5)])
        current = pd.DataFrame(rng.normal(loc=0.5,size=(200,5)), columns=[f"f{i}" for i in range(5)])
        column_mapping = ColumnMapping()
        report = Report(metrics=[DatasetDriftMetric()])
        report.run(reference_data=ref, current_data=current, column_mapping=column_mapping)
        os.makedirs(models_dir, exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report.as_dict(), f, indent=2)
        print("Evidently drift report generated.")
        return 0

def main() -> int:
        return run_drift_monitor()

if __name__ == '__main__':
        sys.exit(main())