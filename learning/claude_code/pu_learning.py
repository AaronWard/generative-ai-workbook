"""
PU Learning Classifier
======================
Positive-Unlabeled (PU) Learning trains a binary classifier when only
positive examples are labeled — the rest are "unlabeled" (a mix of
positives and negatives).

Approach: PU Bagging (Mordelet & Vert, 2014)
- Train N base classifiers, each using:
    * All labeled positives
    * A random subsample of unlabeled examples (treated as negatives)
- Average predictions across all classifiers

Dataset: UCI Breast Cancer Wisconsin (downloaded via sklearn, saved to data/)
- Malignant tumors → Positive (P)
- Benign tumors → hidden in Unlabeled (U); some are exposed as labeled P
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import StandardScaler


# ── Dataset ───────────────────────────────────────────────────────────────────

def download_and_save_dataset(data_dir: Path) -> pd.DataFrame:
    """Load breast cancer dataset and save it to CSV."""
    data_dir.mkdir(parents=True, exist_ok=True)
    csv_path = data_dir / "breast_cancer.csv"

    if csv_path.exists():
        print(f"Dataset already exists at {csv_path}")
        return pd.read_csv(csv_path)

    print("Downloading breast cancer dataset via sklearn...")
    raw = load_breast_cancer()
    df = pd.DataFrame(raw.data, columns=raw.feature_names)
    # 1 = malignant (positive class), 0 = benign
    # sklearn labels: 0=malignant, 1=benign — flip so 1=malignant
    df["label"] = (raw.target == 0).astype(int)
    df.to_csv(csv_path, index=False)
    print(f"Saved {len(df)} samples to {csv_path}")
    return df


# ── PU Learning ───────────────────────────────────────────────────────────────

class PUBaggingClassifier:
    """
    PU Bagging classifier.

    Parameters
    ----------
    n_estimators : int
        Number of base classifiers to train.
    unlabeled_sample_ratio : float
        Fraction of unlabeled examples to use as negatives in each round.
    base_estimator : sklearn estimator
        The base classifier (default: RandomForestClassifier).
    random_state : int
    """

    def __init__(
        self,
        n_estimators: int = 50,
        unlabeled_subsample: int | None = None,
        base_estimator=None,
        random_state: int = 42,
    ):
        self.n_estimators = n_estimators
        # If None, sample same number as positives per round (recommended)
        self.unlabeled_subsample = unlabeled_subsample
        self.base_estimator = base_estimator or RandomForestClassifier(
            n_estimators=10, random_state=random_state
        )
        self.random_state = random_state
        self.estimators_: list = []

    def fit(self, X_pos: np.ndarray, X_unlabeled: np.ndarray) -> "PUBaggingClassifier":
        """
        Train PU bagging ensemble.

        Parameters
        ----------
        X_pos : array of shape (n_positive, n_features)
            Labeled positive examples.
        X_unlabeled : array of shape (n_unlabeled, n_features)
            Unlabeled examples (treated as candidate negatives).
        """
        rng = np.random.default_rng(self.random_state)
        # Default: sample same count as positives to balance each mini-batch
        n_neg_sample = self.unlabeled_subsample or len(X_pos)
        n_neg_sample = min(n_neg_sample, len(X_unlabeled))

        self.estimators_ = []
        for _ in range(self.n_estimators):
            # Sample negatives from unlabeled pool
            idx = rng.choice(len(X_unlabeled), size=n_neg_sample, replace=False)
            X_neg = X_unlabeled[idx]

            X_train = np.vstack([X_pos, X_neg])
            y_train = np.hstack([
                np.ones(len(X_pos)),
                np.zeros(len(X_neg)),
            ])

            # Clone-like: create a fresh estimator each round
            from sklearn.base import clone
            est = clone(self.base_estimator)
            est.set_params(random_state=int(rng.integers(0, 10_000)))
            est.fit(X_train, y_train)
            self.estimators_.append(est)

        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Average positive-class probability across all estimators."""
        probs = np.mean(
            [est.predict_proba(X)[:, 1] for est in self.estimators_], axis=0
        )
        return probs

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        return (self.predict_proba(X) >= threshold).astype(int)

    def find_threshold(
        self, X_val: np.ndarray, y_val: np.ndarray, metric: str = "f1"
    ) -> float:
        """
        Find the probability threshold that maximises F1 (or accuracy)
        on a validation set.  Useful because PU probabilities are not
        well-calibrated to 0.5.
        """
        from sklearn.metrics import f1_score, accuracy_score
        score_fn = f1_score if metric == "f1" else accuracy_score
        probs = self.predict_proba(X_val)
        best_thresh, best_score = 0.5, 0.0
        for t in np.linspace(0.1, 0.9, 81):
            preds = (probs >= t).astype(int)
            s = score_fn(y_val, preds)
            if s > best_score:
                best_score, best_thresh = s, float(t)
        return best_thresh


# ── PU scenario setup ─────────────────────────────────────────────────────────

def create_pu_scenario(
    X: np.ndarray,
    y: np.ndarray,
    label_rate: float = 0.3,
    random_state: int = 42,
):
    """
    Simulate a PU scenario from a fully-labeled dataset.

    - Randomly select `label_rate` fraction of true positives to keep labeled.
    - Move remaining positives + all negatives into the unlabeled pool.

    Returns
    -------
    X_pos      : labeled positive examples
    X_unlabeled: unlabeled pool (hidden positives + all negatives)
    X_test, y_test : held-out test set with true labels
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )

    pos_idx = np.where(y_train == 1)[0]
    rng = np.random.default_rng(random_state)
    n_labeled = max(1, int(len(pos_idx) * label_rate))
    labeled_idx = rng.choice(pos_idx, size=n_labeled, replace=False)

    X_pos = X_train[labeled_idx]
    unlabeled_mask = np.ones(len(X_train), dtype=bool)
    unlabeled_mask[labeled_idx] = False
    X_unlabeled = X_train[unlabeled_mask]

    print(f"\nPU scenario:")
    print(f"  Labeled positives  : {len(X_pos)}")
    print(f"  Unlabeled examples : {len(X_unlabeled)}  "
          f"(includes {len(pos_idx) - n_labeled} hidden positives)")
    print(f"  Test set           : {len(X_test)} (fully labeled for evaluation)")

    return X_pos, X_unlabeled, X_test, y_test


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    data_dir = Path("data")
    df = download_and_save_dataset(data_dir)

    feature_cols = [c for c in df.columns if c != "label"]
    X = df[feature_cols].values
    y = df["label"].values

    # Normalize features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # Build PU scenario
    X_pos, X_unlabeled, X_test, y_test = create_pu_scenario(
        X, y, label_rate=0.3
    )

    # Hold out a small validation split from unlabeled for threshold tuning
    # (in real PU settings you'd use the unlabeled set itself; here we peek
    #  at true labels only to pick the threshold — not used in training)
    val_size = max(20, int(0.15 * len(X_test)))
    X_val, X_eval = X_test[:val_size], X_test[val_size:]
    y_val, y_eval = y_test[:val_size], y_test[val_size:]

    # Train PU Bagging
    print("\nTraining PU Bagging classifier (balanced subsample per round)...")
    pu_clf = PUBaggingClassifier(n_estimators=100)
    pu_clf.fit(X_pos, X_unlabeled)

    # Calibrate threshold on validation split
    best_thresh = pu_clf.find_threshold(X_val, y_val)
    print(f"Optimal threshold (val F1): {best_thresh:.2f}")

    # Evaluate on held-out eval set
    y_pred = pu_clf.predict(X_eval, threshold=best_thresh)
    y_prob = pu_clf.predict_proba(X_eval)

    print("\nPU Bagging — Test Set Results:")
    print(classification_report(y_eval, y_pred, target_names=["Benign", "Malignant"],
                                zero_division=0))
    print(f"ROC-AUC: {roc_auc_score(y_eval, y_prob):.4f}")

    # Baseline: naive RF with all unlabeled treated as negatives (no bagging)
    print("\nBaseline (naive): single RF, unlabeled = negatives")
    X_naive = np.vstack([X_pos, X_unlabeled])
    y_naive = np.hstack([np.ones(len(X_pos)), np.zeros(len(X_unlabeled))])
    naive_clf = RandomForestClassifier(n_estimators=100, random_state=42)
    naive_clf.fit(X_naive, y_naive)
    y_prob_naive = naive_clf.predict_proba(X_eval)[:, 1]
    best_thresh_naive = float(np.median(y_prob_naive))
    y_pred_naive = (y_prob_naive >= best_thresh_naive).astype(int)
    print(classification_report(y_eval, y_pred_naive, target_names=["Benign", "Malignant"],
                                zero_division=0))
    print(f"ROC-AUC: {roc_auc_score(y_eval, y_prob_naive):.4f}")


if __name__ == "__main__":
    main()
