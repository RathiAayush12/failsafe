"""
FailSafe — Model Training
XGBoost Classifier with Hyperparameter Tuning
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import (
    classification_report, roc_auc_score,
    confusion_matrix, f1_score, precision_score, recall_score
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold
import joblib
import json
import os

MODEL_DIR = "data/processed"
OUTPUT_DIR = "data/model"


def load_splits(data_dir: str = MODEL_DIR):
    X_train = pd.read_csv(f"{data_dir}/X_train.csv")
    X_val = pd.read_csv(f"{data_dir}/X_val.csv")
    X_test = pd.read_csv(f"{data_dir}/X_test.csv")
    y_train = pd.read_csv(f"{data_dir}/y_train.csv").squeeze()
    y_val = pd.read_csv(f"{data_dir}/y_val.csv").squeeze()
    y_test = pd.read_csv(f"{data_dir}/y_test.csv").squeeze()
    return X_train, X_val, X_test, y_train, y_val, y_test


def train_model(X_train, y_train, X_val, y_val, tune: bool = False):
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

    if tune:
        param_grid = {
            "n_estimators": [100, 200, 300],
            "max_depth": [3, 5, 7],
            "learning_rate": [0.01, 0.05, 0.1],
            "subsample": [0.7, 0.9],
            "colsample_bytree": [0.7, 0.9],
        }
        base_model = xgb.XGBClassifier(
            scale_pos_weight=scale_pos_weight,
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=42
        )
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        grid = GridSearchCV(base_model, param_grid, cv=cv, scoring="f1", n_jobs=-1, verbose=1)
        grid.fit(X_train, y_train)
        model = grid.best_estimator_
        print(f"Best params: {grid.best_params_}")
    else:
        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.8,
            scale_pos_weight=scale_pos_weight,
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=42,
            early_stopping_rounds=20
        )
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )

    return model


def evaluate_model(model, X, y, split_name: str = "Test"):
    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)[:, 1]

    metrics = {
        "split": split_name,
        "roc_auc": round(roc_auc_score(y, y_prob), 4),
        "f1": round(f1_score(y, y_pred), 4),
        "precision": round(precision_score(y, y_pred), 4),
        "recall": round(recall_score(y, y_pred), 4),
    }

    print(f"\n{'='*40}")
    print(f"Evaluation — {split_name}")
    print(f"{'='*40}")
    print(f"ROC-AUC:   {metrics['roc_auc']}")
    print(f"F1 Score:  {metrics['f1']}")
    print(f"Precision: {metrics['precision']}")
    print(f"Recall:    {metrics['recall']}")
    print("\nClassification Report:")
    print(classification_report(y, y_pred, target_names=["Not at risk", "At risk"]))
    print("Confusion Matrix:")
    print(confusion_matrix(y, y_pred))

    return metrics


def get_feature_importances(model, feature_cols: list) -> dict:
    importances = model.feature_importances_
    fi = dict(zip(feature_cols, importances.tolist()))
    return dict(sorted(fi.items(), key=lambda x: x[1], reverse=True))


def save_model(model, feature_cols: list, metrics: dict, output_dir: str = OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    joblib.dump(model, f"{output_dir}/model.pkl")
    joblib.dump(feature_cols, f"{output_dir}/feature_cols.pkl")
    with open(f"{output_dir}/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nModel saved to {output_dir}/model.pkl")


if __name__ == "__main__":
    X_train, X_val, X_test, y_train, y_val, y_test = load_splits()
    feature_cols = joblib.load(f"{MODEL_DIR}/feature_cols.pkl")

    print("Training XGBoost model...")
    model = train_model(X_train, y_train, X_val, y_val, tune=False)

    val_metrics = evaluate_model(model, X_val, y_val, "Validation")
    test_metrics = evaluate_model(model, X_test, y_test, "Test")

    fi = get_feature_importances(model, feature_cols)
    print("\nTop 10 feature importances:")
    for feat, imp in list(fi.items())[:10]:
        print(f"  {feat}: {imp:.4f}")

    save_model(model, feature_cols, {"val": val_metrics, "test": test_metrics})
