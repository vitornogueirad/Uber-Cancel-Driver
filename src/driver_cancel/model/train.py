import warnings, joblib
import numpy as np, pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import (average_precision_score, roc_auc_score, f1_score,
    precision_recall_curve, classification_report, confusion_matrix)
from sklearn.calibration import CalibratedClassifierCV
from lightgbm import LGBMClassifier

from ..core.config import settings
from ..features.transforms import cap_categorias, add_time_features
from ..utils.io import save_json

warnings.filterwarnings("ignore")
SEED = settings.seed

def main():
    df = pd.read_csv(settings.data_path)
    df = add_time_features(df, "Date", "Time")

    y = (df["Booking Status"].eq("Cancelled by Driver")).astype("int8")

    cat_cols_raw = [c for c in ["Pickup Location", "Drop Location", "Vehicle Type", "Payment Method"] if c in df.columns]
    num_cols_raw = [c for c in ["Avg VTAT"] if c in df.columns]
    use_cols = [*cat_cols_raw, *num_cols_raw, "hour", "day_of_week", "is_weekend"]
    X = df[use_cols].copy()

    for c in cat_cols_raw:
        X[c] = cap_categorias(X[c].fillna("Unknown"), k=30)

    X_train, X_tmp, y_train, y_tmp = train_test_split(X, y, test_size=0.30, stratify=y, random_state=SEED)
    X_val, X_test, y_val, y_test = train_test_split(X_tmp, y_tmp, test_size=0.50, stratify=y_tmp, random_state=SEED)

    cat_cols = [c for c in X_train.columns if X_train[c].dtype == "O"]
    num_cols = [c for c in X_train.columns if c not in cat_cols]

    pre = ColumnTransformer([
        ("cat", Pipeline([
            ("imp", SimpleImputer(strategy="most_frequent")),
            ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ]), cat_cols),
        ("num", Pipeline([
            ("imp", SimpleImputer(strategy="median"))
        ]), num_cols)
    ])

    pos = y_train.sum(); neg = len(y_train) - pos
    spw = (neg / max(pos, 1))

    clf = Pipeline([
        ("pre", pre),
        ("lgbm", LGBMClassifier(
            n_estimators=600,
            learning_rate=0.05, 
            num_leaves=63,
            min_child_samples=40, 
            subsample=0.9, 
            colsample_bytree=0.9,
            reg_lambda=1.0, 
            random_state=SEED, 
            scale_pos_weight=spw,
            n_jobs=-1, verbose=-1
        ))
    ])

    cal = CalibratedClassifierCV(clf, cv=5, method="isotonic")
    cal.fit(X_train, y_train)

    proba_val = cal.predict_proba(X_val)[:, 1]
    prec, rec, thr = precision_recall_curve(y_val, proba_val)
    f1s = (2 * prec * rec) / (prec + rec + 1e-12)
    thr_star = float(thr[(f1s[:-1]).argmax()]) if len(thr) else 0.5

    proba_test = cal.predict_proba(X_test)[:, 1]
    pred_test = (proba_test >= thr_star).astype(int)

    print("Prevalência teste:", round(y_test.mean(), 3))
    print("PR-AUC:", round(average_precision_score(y_test, proba_test), 4))
    print("ROC-AUC:", round(roc_auc_score(y_test, proba_test), 4))
    print(f"F1 @ thr*={thr_star:.3f}:", round(f1_score(y_test, pred_test), 4))
    print("\nClassification report:\n", classification_report(y_test, pred_test, digits=3))
    print("Confusion matrix:\n", confusion_matrix(y_test, pred_test))

    art = Path(settings.artifact_dir); art.mkdir(parents=True, exist_ok=True)
    joblib.dump(cal, art / "uber_cancel_driver_clf.joblib")
    save_json({"feature_order": use_cols,
               "categorical": cat_cols_raw,
               "numeric_time": ["hour", "day_of_week", "is_weekend"]},
              str(art / "model_schema.json"))
    save_json({"threshold": thr_star}, str(art / "threshold.json"))
    print(f"\nArtefatos salvos em {art.resolve()}")

if __name__ == "__main__":
    main()
