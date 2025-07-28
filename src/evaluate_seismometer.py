"""
evaluate_seismometer.py
    
Run Seismometer evaluation on the trained model.  Seismometer is a
performance evaluation tool.  If the library is unavailable, this
script prints a warning and exits gracefully.  Evaluation results are
stored in the models directory for further analysis.
"""
    
import json
import os
import sys
    
    
def run_seismometer() -> int:
        models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
        metrics_path = os.path.join(models_dir, 'metrics.json')
        results_path = os.path.join(models_dir, 'seismometer.json')
        if not os.path.exists(metrics_path):
            print("Training metrics not found. Run train_model.py first.", file=sys.stderr)
            return 1
        try:
            import seismometer  # type: ignore
        except ImportError:
            print(
                "Seismometer library not installed; skipping evaluation.",
                file=sys.stderr,
            )
            return 1
        try:
            from seismometer import Seismometer
            with open(metrics_path) as f:
                baseline_metrics = json.load(f)
            # Create a simple report using baseline metrics
            sm = Seismometer()
            report = sm.evaluate(baseline_metrics)
            with open(results_path, 'w') as f:
                json.dump(report, f, indent=2)
            print("Seismometer evaluation complete.")
            return 0
        except Exception as e:
            print(f"Error running Seismometer: {e}", file=sys.stderr)
            return 1
    
    
def main() -> int:
        return run_seismometer()
    
    
if __name__ == '__main__':
        sys.exit(main())