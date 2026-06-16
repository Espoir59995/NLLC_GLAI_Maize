#!/usr/bin/env python3
"""
Train a Random Forest classifier for maize leaf component classification.

The model uses pixel-level B, G, R values as input features and predicts four
classes used in the manuscript:

    1 = white background
    2 = red reference square
    3 = green photosynthetic leaf component
    4 = yellow non-photosynthetic leaf component

Example
-------
python scripts/train_rf_leaf_component_classifier.py \
    --training-csv data/training_pixels/3GreenandYellow.csv \
    --model-out model/3GreenandYellow.pkl \
    --metrics-out outputs_example/rf_cross_validation_metrics.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold


DEFAULT_CLASS_NAMES = {
    1: "background",
    2: "red_reference_square",
    3: "green_photosynthetic_leaf_component",
    4: "yellow_non_photosynthetic_leaf_component",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Train a Random Forest classifier using pixel-level B, G, R values "
            "for maize leaf component classification."
        )
    )
    parser.add_argument(
        "--training-csv",
        required=True,
        type=Path,
        help="Path to the pixel-level training CSV file. Required columns are B, G, R, and TYPE by default.",
    )
    parser.add_argument(
        "--model-out",
        default=Path("model/3GreenandYellow.pkl"),
        type=Path,
        help="Output path for the trained Random Forest model (.pkl).",
    )
    parser.add_argument(
        "--metrics-out",
        default=Path("outputs_example/rf_cross_validation_metrics.csv"),
        type=Path,
        help="Output CSV path for cross-validation metrics.",
    )
    parser.add_argument(
        "--metadata-out",
        default=Path("model/3GreenandYellow_model_metadata.json"),
        type=Path,
        help="Output JSON path for model metadata.",
    )
    parser.add_argument(
        "--feature-columns",
        nargs=3,
        default=["B", "G", "R"],
        help="Feature column names in the training CSV. Default: B G R.",
    )
    parser.add_argument(
        "--label-column",
        default="TYPE",
        help="Label column name in the training CSV. Default: TYPE.",
    )
    parser.add_argument(
        "--n-estimators",
        type=int,
        default=300,
        help="Number of trees in the Random Forest. Default: 300.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Maximum tree depth. Default: None.",
    )
    parser.add_argument(
        "--n-splits",
        type=int,
        default=5,
        help="Number of folds for stratified cross-validation. Default: 5.",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random seed for reproducibility. Default: 42.",
    )
    return parser.parse_args()


def validate_columns(data: pd.DataFrame, feature_columns: List[str], label_column: str) -> None:
    required = set(feature_columns + [label_column])
    missing = sorted(required.difference(data.columns))
    if missing:
        raise ValueError(
            f"Missing required column(s) in training CSV: {missing}. "
            f"Available columns: {list(data.columns)}"
        )


def run_cross_validation(
    x: np.ndarray,
    y: np.ndarray,
    n_splits: int,
    random_state: int,
    n_estimators: int,
    max_depth: int | None,
) -> pd.DataFrame:
    class_counts = pd.Series(y).value_counts()
    min_class_count = int(class_counts.min())
    if n_splits > min_class_count:
        raise ValueError(
            f"n_splits={n_splits} is larger than the smallest class count ({min_class_count}). "
            "Reduce --n-splits or add more labelled pixels for the rarest class."
        )

    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    rows = []

    for fold_id, (train_idx, val_idx) in enumerate(cv.split(x, y), start=1):
        clf = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,
            class_weight=None,
        )
        clf.fit(x[train_idx], y[train_idx])
        pred = clf.predict(x[val_idx])

        rows.append(
            {
                "fold": fold_id,
                "accuracy": accuracy_score(y[val_idx], pred),
                "precision_macro": precision_score(y[val_idx], pred, average="macro", zero_division=0),
                "recall_macro": recall_score(y[val_idx], pred, average="macro", zero_division=0),
                "f1_macro": f1_score(y[val_idx], pred, average="macro", zero_division=0),
            }
        )

    metrics = pd.DataFrame(rows)
    mean_row = {"fold": "mean"}
    for column in ["accuracy", "precision_macro", "recall_macro", "f1_macro"]:
        mean_row[column] = metrics[column].mean()
    metrics = pd.concat([metrics, pd.DataFrame([mean_row])], ignore_index=True)
    return metrics


def main() -> None:
    args = parse_args()

    if not args.training_csv.exists():
        raise FileNotFoundError(f"Training CSV not found: {args.training_csv}")

    data = pd.read_csv(args.training_csv)
    validate_columns(data, args.feature_columns, args.label_column)

    x = data[args.feature_columns].to_numpy(dtype=np.uint8)
    y = data[args.label_column].to_numpy().ravel()

    metrics = run_cross_validation(
        x=x,
        y=y,
        n_splits=args.n_splits,
        random_state=args.random_state,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
    )

    args.metrics_out.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.metrics_out, index=False)

    final_model = RandomForestClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        random_state=args.random_state,
        n_jobs=-1,
        class_weight=None,
    )
    final_model.fit(x, y)

    args.model_out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_model, args.model_out)

    metadata = {
        "model_type": "RandomForestClassifier",
        "feature_columns": args.feature_columns,
        "label_column": args.label_column,
        "class_labels": DEFAULT_CLASS_NAMES,
        "n_estimators": args.n_estimators,
        "max_depth": args.max_depth,
        "n_splits": args.n_splits,
        "random_state": args.random_state,
        "training_csv": str(args.training_csv),
        "n_training_pixels": int(len(y)),
        "class_counts": {str(k): int(v) for k, v in pd.Series(y).value_counts().sort_index().items()},
        "metrics_file": str(args.metrics_out),
    }
    args.metadata_out.parent.mkdir(parents=True, exist_ok=True)
    args.metadata_out.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    mean_metrics = metrics[metrics["fold"] == "mean"].iloc[0]
    print("Training completed.")
    print(f"Model saved to: {args.model_out}")
    print(f"Cross-validation metrics saved to: {args.metrics_out}")
    print(
        "Mean metrics: "
        f"accuracy={mean_metrics['accuracy']:.4f}, "
        f"precision_macro={mean_metrics['precision_macro']:.4f}, "
        f"recall_macro={mean_metrics['recall_macro']:.4f}, "
        f"f1_macro={mean_metrics['f1_macro']:.4f}"
    )


if __name__ == "__main__":
    main()
