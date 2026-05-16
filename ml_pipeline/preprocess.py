"""
FailSafe — Data Preprocessing
UCI Student Performance Dataset
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

FEATURE_COLUMNS = [
    "school", "sex", "age", "address", "famsize", "Pstatus",
    "Medu", "Fedu", "Mjob", "Fjob", "reason", "guardian",
    "traveltime", "studytime", "failures", "schoolsup", "famsup",
    "paid", "activities", "nursery", "higher", "internet",
    "romantic", "famrel", "freetime", "goout", "Dalc", "Walc",
    "health", "absences"
]

BINARY_COLS = [
    "school", "sex", "address", "famsize", "Pstatus",
    "schoolsup", "famsup", "paid", "activities", "nursery",
    "higher", "internet", "romantic"
]

CATEGORICAL_COLS = ["Mjob", "Fjob", "reason", "guardian"]


def load_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, sep=";")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Target: at-risk if final grade G3 < 10
    df["at_risk"] = (df["G3"] < 10).astype(int)

    # Aggregate grade trend
    df["grade_trend"] = df["G3"] - df["G1"]
    df["avg_grade"] = (df["G1"] + df["G2"] + df["G3"]) / 3

    # Alcohol index
    df["alcohol_index"] = (df["Dalc"] * 2 + df["Walc"]) / 3

    # Study efficiency
    df["study_efficiency"] = df["studytime"] / (df["failures"] + 1)

    # Absence severity buckets
    df["absence_level"] = pd.cut(
        df["absences"], bins=[-1, 0, 5, 15, 100],
        labels=[0, 1, 2, 3]
    ).astype(int)

    return df


def encode_features(df: pd.DataFrame, encoders: dict = None, fit: bool = True):
    df = df.copy()
    if encoders is None:
        encoders = {}

    for col in BINARY_COLS:
        le = LabelEncoder()
        if fit:
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
        else:
            df[col] = encoders[col].transform(df[col].astype(str))

    for col in CATEGORICAL_COLS:
        dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
        df = pd.concat([df, dummies], axis=1)
        df.drop(col, axis=1, inplace=True)

    return df, encoders


def get_feature_columns(df: pd.DataFrame) -> list:
    exclude = ["G1", "G2", "G3", "at_risk"]
    return [c for c in df.columns if c not in exclude]


def preprocess_pipeline(filepath: str, output_dir: str = "data/processed"):
    os.makedirs(output_dir, exist_ok=True)

    df = load_data(filepath)
    df = engineer_features(df)
    df, encoders = encode_features(df)

    feature_cols = get_feature_columns(df)
    X = df[feature_cols]
    y = df["at_risk"]

    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=feature_cols)
    X_val_scaled = pd.DataFrame(scaler.transform(X_val), columns=feature_cols)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=feature_cols)

    # Save splits
    X_train_scaled.to_csv(f"{output_dir}/X_train.csv", index=False)
    X_val_scaled.to_csv(f"{output_dir}/X_val.csv", index=False)
    X_test_scaled.to_csv(f"{output_dir}/X_test.csv", index=False)
    y_train.to_csv(f"{output_dir}/y_train.csv", index=False)
    y_val.to_csv(f"{output_dir}/y_val.csv", index=False)
    y_test.to_csv(f"{output_dir}/y_test.csv", index=False)

    joblib.dump(encoders, f"{output_dir}/encoders.pkl")
    joblib.dump(scaler, f"{output_dir}/scaler.pkl")
    joblib.dump(feature_cols, f"{output_dir}/feature_cols.pkl")

    print(f"Preprocessing complete. Features: {len(feature_cols)}")
    print(f"Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")
    print(f"At-risk rate: {y.mean():.2%}")

    return X_train_scaled, X_val_scaled, X_test_scaled, y_train, y_val, y_test, feature_cols


if __name__ == "__main__":
    preprocess_pipeline("data/student-mat.csv")
