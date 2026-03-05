"""Visualize PU Learning results."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve, auc
from sklearn.decomposition import PCA

from pu_learning import PUBaggingClassifier

# ── Reproduce experiment ──────────────────────────────────────────────────────

df = pd.read_csv("data/breast_cancer.csv")
feature_cols = [c for c in df.columns if c != "label"]
X_raw = df[feature_cols].values
y = df["label"].values

scaler = StandardScaler()
X = scaler.fit_transform(X_raw)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

pos_idx = np.where(y_train == 1)[0]
rng = np.random.default_rng(42)
n_labeled = max(1, int(len(pos_idx) * 0.3))
labeled_idx = rng.choice(pos_idx, size=n_labeled, replace=False)

X_pos = X_train[labeled_idx]
unlabeled_mask = np.ones(len(X_train), dtype=bool)
unlabeled_mask[labeled_idx] = False
X_unlabeled = X_train[unlabeled_mask]
y_unlabeled_true = y_train[unlabeled_mask]

# Train PU Bagging
pu_clf = PUBaggingClassifier(n_estimators=100)
pu_clf.fit(X_pos, X_unlabeled)

val_size = max(20, int(0.15 * len(X_test)))
X_val, y_val = X_test[:val_size], y_test[:val_size]
X_eval, y_eval = X_test[val_size:], y_test[val_size:]
best_thresh = pu_clf.find_threshold(X_val, y_val)

# PU predictions on unlabeled pool
prob_unlabeled = pu_clf.predict_proba(X_unlabeled)
pred_unlabeled = pu_clf.predict(X_unlabeled, threshold=best_thresh)

# Naive baseline
X_naive = np.vstack([X_pos, X_unlabeled])
y_naive = np.hstack([np.ones(len(X_pos)), np.zeros(len(X_unlabeled))])
naive_clf = RandomForestClassifier(n_estimators=100, random_state=42)
naive_clf.fit(X_naive, y_naive)

# ROC curves on eval set
prob_pu   = pu_clf.predict_proba(X_eval)
prob_base = naive_clf.predict_proba(X_eval)[:, 1]
fpr_pu,   tpr_pu,   _ = roc_curve(y_eval, prob_pu)
fpr_base, tpr_base, _ = roc_curve(y_eval, prob_base)
auc_pu   = auc(fpr_pu, tpr_pu)
auc_base = auc(fpr_base, tpr_base)

# PCA for 2-D scatter
pca = PCA(n_components=2, random_state=42)
X_train_2d  = pca.fit_transform(X_train)
X_unlabeled_2d = X_train_2d[unlabeled_mask]
X_pos_2d       = X_train_2d[labeled_idx]

# ── Plot ──────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(13, 10))
fig.suptitle("PU Learning — Breast Cancer Dataset", fontsize=15, fontweight="bold", y=1.01)

BLUE   = "#4C72B0"
RED    = "#DD4949"
GREEN  = "#2CA02C"
ORANGE = "#FF7F0E"
GREY   = "#AAAAAA"

# ── 1. PU Scenario (PCA scatter) ──────────────────────────────────────────────
ax = axes[0, 0]

hidden_pos_mask  = y_unlabeled_true == 1
hidden_neg_mask  = y_unlabeled_true == 0

ax.scatter(*X_unlabeled_2d[hidden_neg_mask].T, s=18, color=GREY,   alpha=0.5, label="Unlabeled (benign)")
ax.scatter(*X_unlabeled_2d[hidden_pos_mask].T, s=18, color=BLUE,   alpha=0.5, label="Unlabeled (hidden malignant)")
ax.scatter(*X_pos_2d.T,                        s=45, color=RED,    alpha=0.9, marker="*", label=f"Labeled positive (n={len(X_pos)})")

ax.set_title("PU Scenario (PCA projection)", fontweight="bold")
ax.set_xlabel("PC 1"); ax.set_ylabel("PC 2")
ax.legend(fontsize=8, loc="upper right")

# ── 2. Recovery results (stacked bar) ────────────────────────────────────────
ax = axes[0, 1]

hidden_pos  = hidden_pos_mask.sum()
recovered   = int(((pred_unlabeled == 1) & (y_unlabeled_true == 1)).sum())
missed      = int(hidden_pos - recovered)
false_pos   = int(((pred_unlabeled == 1) & (y_unlabeled_true == 0)).sum())
true_neg    = int(((pred_unlabeled == 0) & (y_unlabeled_true == 0)).sum())

categories  = ["True Positives\n(hidden malignant)", "True Negatives\n(benign)"]
correct     = [recovered,  true_neg]
incorrect   = [missed,     false_pos]

x = np.arange(len(categories))
w = 0.45
b1 = ax.bar(x, correct,   width=w, color=[GREEN, GREEN], label="Correct",   alpha=0.85)
b2 = ax.bar(x, incorrect, width=w, bottom=correct, color=[RED, ORANGE],
            label=["Missed", "False positive"], alpha=0.85)

for bar, val in zip(b1, correct):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
            str(val), ha="center", va="center", fontweight="bold", color="white", fontsize=12)
for bar, bot, val in zip(b2, correct, incorrect):
    if val > 0:
        ax.text(bar.get_x() + bar.get_width()/2, bot + val/2,
                str(val), ha="center", va="center", fontweight="bold", color="white", fontsize=12)

ax.set_xticks(x); ax.set_xticklabels(categories, fontsize=9)
ax.set_ylabel("Count")
ax.set_title(f"Recovery from Unlabeled Pool\n(threshold = {best_thresh:.2f})", fontweight="bold")
green_patch  = mpatches.Patch(color=GREEN,  label="Correctly classified")
red_patch    = mpatches.Patch(color=RED,    label="Missed positives")
orange_patch = mpatches.Patch(color=ORANGE, label="False positives")
ax.legend(handles=[green_patch, red_patch, orange_patch], fontsize=8)

# ── 3. Probability distribution on unlabeled pool ────────────────────────────
ax = axes[1, 0]

bins = np.linspace(0, 1, 35)
ax.hist(prob_unlabeled[hidden_neg_mask],  bins=bins, color=GREY,  alpha=0.65, label="True benign")
ax.hist(prob_unlabeled[hidden_pos_mask],  bins=bins, color=BLUE,  alpha=0.65, label="True malignant (hidden)")
ax.axvline(best_thresh, color=RED, linestyle="--", linewidth=1.8, label=f"Threshold ({best_thresh:.2f})")

ax.set_xlabel("Predicted probability (malignant)")
ax.set_ylabel("Count")
ax.set_title("Score Distribution — Unlabeled Pool", fontweight="bold")
ax.legend(fontsize=8)

# ── 4. ROC curve comparison ───────────────────────────────────────────────────
ax = axes[1, 1]

ax.plot(fpr_pu,   tpr_pu,   color=BLUE,   lw=2, label=f"PU Bagging  (AUC = {auc_pu:.4f})")
ax.plot(fpr_base, tpr_base, color=ORANGE, lw=2, linestyle="--", label=f"Naive RF    (AUC = {auc_base:.4f})")
ax.plot([0, 1], [0, 1], color=GREY, lw=1, linestyle=":")

ax.set_xlabel("False Positive Rate"); ax.set_ylabel("True Positive Rate")
ax.set_title("ROC Curve — Test Set", fontweight="bold")
ax.legend(fontsize=9)

# ── Save ──────────────────────────────────────────────────────────────────────
plt.tight_layout()
out = Path("data/pu_results.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"Saved plot to {out}")
plt.show()
