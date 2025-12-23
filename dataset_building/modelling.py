"""
Converted from `modelling.ipynb`.
Generates a 2-week volatility forecast by iteratively retraining an XGBoost regressor
and writes `volatility_forecasted_dataset.csv`.
"""

import os
import pandas as pd
import numpy as np

# Try to import XGBoost, fall back to RandomForest if unavailable to improve robustness
try:
    from xgboost import XGBRegressor
    _HAS_XGBOOST = True
except Exception:
    _HAS_XGBOOST = False
    from sklearn.ensemble import RandomForestRegressor

# ======================================================
# BASE DIR (robuste quel que soit le point d'exécution)
# ======================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# The repository has `dataset_building/final_dataset.csv` at the project level.
# Use the file if present; otherwise fall back to `dataset_building/data/final_dataset.csv`.
DATA_DIR = os.path.join(BASE_DIR, "data")
INPUT_FILE = os.path.join(BASE_DIR, "final_dataset.csv")
if not os.path.exists(INPUT_FILE):
    INPUT_FILE = os.path.join(DATA_DIR, "final_dataset.csv")

# Write the output where the backend expects it: `dataset_building/volatility_forecasted_dataset.csv`.
OUTPUT_FILE = os.path.join(BASE_DIR, "volatility_forecasted_dataset.csv")

os.makedirs(DATA_DIR, exist_ok=True)

# ======================================================
# Dynamic forecasting function
# ======================================================

def dynamic_forecast_with_retraining(df, model_params, target_col="vol_future_2w"):
    """
    Iteratively predict missing values in `target_col` and retrain the model after each prediction.
    """
    df = df.copy()

    if target_col not in df.columns:
        raise ValueError(f"target_col '{target_col}' not in dataframe")

    known_idx = df[~df[target_col].isna()].index
    unknown_idx = df[df[target_col].isna()].index

    X_train_dyn = df.loc[known_idx].drop(columns=[target_col])
    y_train_dyn = df.loc[known_idx, target_col]

    predictions = []

    for idx in unknown_idx:
        if _HAS_XGBOOST:
            model = XGBRegressor(
                **model_params,
                objective="reg:squarederror",
                eval_metric="rmse",
                random_state=42,
                n_jobs=-1,
            )
        else:
            # Fallback to a lightweight RandomForest when XGBoost is not available
            model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)

        # Fit without verbose
        model.fit(X_train_dyn, y_train_dyn)

        X_pred = df.loc[idx].drop(labels=[target_col]).values.reshape(1, -1)
        y_pred = model.predict(X_pred)[0]

        df.loc[idx, target_col] = y_pred
        predictions.append(y_pred)

        # Update lag features if present
        next_idx = idx + 1
        if next_idx in df.index:
            if "vol_future_2w_1" in df.columns:
                df.loc[next_idx, "vol_future_2w_1"] = y_pred
            if "vol_future_2w_2" in df.columns:
                df.loc[next_idx, "vol_future_2w_2"] = (
                    df.loc[idx - 1, target_col]
                    if idx - 1 in df.index
                    else y_pred
                )
            if "vol_future_2w_3" in df.columns:
                df.loc[next_idx, "vol_future_2w_3"] = (
                    df.loc[idx - 2, target_col]
                    if idx - 2 in df.index
                    else y_pred
                )

        X_train_dyn = pd.concat(
            [X_train_dyn, df.loc[[idx]].drop(columns=[target_col])],
            ignore_index=True,
        )
        y_train_dyn = pd.concat(
            [y_train_dyn, pd.Series(y_pred)],
            ignore_index=True,
        )

    return df, predictions

# ======================================================
# Main
# ======================================================

def main():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}. Run dataset processing first."
        )

    df_lagged = pd.read_csv(INPUT_FILE)
    TARGET = "vol_future_2w"

    feature_cols = [
        "vol_future_2w_1",
        "vol_future_2w_2",
        "vol_future_2w_3",
        "Performances glissantes 1 semaine",
        "rendement_lag_1",
        "garch_vol",
        "Variation %",
        TARGET,
    ]

    df_model = df_lagged.loc[:, [c for c in feature_cols if c in df_lagged.columns]].copy()

    numeric_part = df_model.select_dtypes(include=[np.number])
    if TARGET in df_model.columns:
        df_model = pd.concat([numeric_part.drop(columns=[TARGET], errors="ignore"),
                              df_model[[TARGET]]], axis=1)
    else:
        df_model = numeric_part

    best_params = {
        "max_depth": 3,
        "min_child_weight": 5,
        "subsample": 0.8,
        "colsample_bytree": 1,
        "learning_rate": 0.01,
        "n_estimators": 1200,
    }

    df_filled, preds = dynamic_forecast_with_retraining(
        df_model, best_params, target_col=TARGET
    )

    if "Date" in df_lagged.columns:
        df_filled_final = pd.concat(
            [df_lagged[["Date"]].reset_index(drop=True),
             df_filled.reset_index(drop=True)],
            axis=1,
        )
    else:
        df_filled_final = df_filled

    df_filled_final.to_csv(OUTPUT_FILE, index=False)
    # Avoid non-ASCII characters to prevent Windows stdout encoding errors
    print(f"Saved {OUTPUT_FILE} ({len(preds)} predictions)")
    if not _HAS_XGBOOST:
        print("Warning: xgboost not available - used RandomForestRegressor fallback.")


if __name__ == "__main__":
    main()
