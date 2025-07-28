"""
train_model.py
    
Train a simple logistic regression baseline on synthetic data.  The
training procedure uses scikit‑learn and stores both the model
artifact and metrics locally.  This baseline demonstrates how
modeling code should be transparent and reproducible.
"""
    
import os
import pickle
import sys
from typing import Tuple
    
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
    
    
def load_dataset() -> Tuple[np.ndarray, np.ndarray]:
        """Load or synthesise a training dataset.
    
        If a CSV file named ``training.csv`` exists in the data directory it is
        loaded.  Otherwise random data are generated.  This fallback
        ensures the module can run without external dependencies while
        encouraging users to replace it with their own Synthea export.
        """
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        csv_path = os.path.join(data_dir, 'training.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            X = df.drop('target', axis=1).values
            y = df['target'].values
        else:
            # Generate dummy binary classification data
            rng = np.random.default_rng(seed=42)
            X = rng.normal(size=(500, 10))
            y = (X.sum(axis=1) > 0).astype(int)
        return X, y
    
    
def train_model() -> dict:
        X, y = load_dataset()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        clf = LogisticRegression(max_iter=100)
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        y_prob = clf.predict_proba(X_test)[:, 1]
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_prob),
        }
        models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
        os.makedirs(models_dir, exist_ok=True)
        model_path = os.path.join(models_dir, 'logreg.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(clf, f)
        metrics_path = os.path.join(models_dir, 'metrics.json')
        import json
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"Model trained. Accuracy: {metrics['accuracy']:.3f}, ROC AUC: {metrics['roc_auc']:.3f}")
        return metrics
    
    
def main() -> int:
        try:
            train_model()
            return 0
        except Exception as e:
            print(f"Error training model: {e}", file=sys.stderr)
            return 1
    
    
if __name__ == '__main__':
        sys.exit(main())