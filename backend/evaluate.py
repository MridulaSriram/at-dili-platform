"""Metrics and plots used to judge a risk model."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.special import logit
from sklearn.metrics import roc_auc_score, brier_score_loss, roc_curve
from sklearn.linear_model import LogisticRegression


def auc_ci(y, p, n_boot=500, seed=1):
    rng = np.random.default_rng(seed)
    y, p = np.asarray(y), np.asarray(p)
    base = roc_auc_score(y, p)
    vals = []
    for _ in range(n_boot):
        i = rng.integers(0, len(y), len(y))
        if y[i].min() == y[i].max():
            continue
        vals.append(roc_auc_score(y[i], p[i]))
    return base, np.percentile(vals, 2.5), np.percentile(vals, 97.5)


def calibration_slope_intercept(y, p):
    """
    Slope near 1 and intercept near 0 mean good calibration.
    Slope < 1: predictions too extreme (overfitting or a poor transfer).
    Intercept is estimated with the slope fixed at 1 (calibration-in-the-large).
    """
    p = np.clip(np.asarray(p), 1e-6, 1 - 1e-6)
    lp = logit(p).reshape(-1, 1)
    m = LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000).fit(lp, y)
    slope = float(m.coef_[0, 0])
    # intercept with offset: use the mean-difference identity as a simple check
    citl = float(np.log(np.mean(y) / (1 - np.mean(y)))
                 - np.log(np.mean(p) / (1 - np.mean(p))))
    return slope, citl


def summary_row(name, y, p):
    a, lo, hi = auc_ci(y, p)
    s, c = calibration_slope_intercept(y, p)
    return dict(model=name, AUC=a, AUC_lo=lo, AUC_hi=hi,
                Brier=brier_score_loss(y, p), calib_slope=s, calib_in_large=c,
                mean_pred=float(np.mean(p)), observed=float(np.mean(y)))


def net_benefit(y, p, thresholds):
    y, p = np.asarray(y), np.asarray(p)
    n = len(y)
    out = []
    for t in thresholds:
        pred = p >= t
        tp = ((pred) & (y == 1)).sum()
        fp = ((pred) & (y == 0)).sum()
        out.append(tp / n - fp / n * t / (1 - t))
    return np.array(out)


def plot_roc(preds, y, path):
    plt.figure(figsize=(5.5, 5))
    for name, p in preds.items():
        fpr, tpr, _ = roc_curve(y, p)
        plt.plot(fpr, tpr, label=f"{name} (AUC {roc_auc_score(y, p):.2f})")
    plt.plot([0, 1], [0, 1], "k:", lw=1)
    plt.xlabel("1 - specificity"); plt.ylabel("Sensitivity")
    plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(path, dpi=150); plt.close()


def plot_calibration(preds, y, path, bins=8):
    plt.figure(figsize=(5.5, 5))
    for name, p in preds.items():
        d = pd.DataFrame({"y": y, "p": p})
        d["bin"] = pd.qcut(d["p"], bins, duplicates="drop")
        g = d.groupby("bin", observed=True).agg(p=("p", "mean"), y=("y", "mean"))
        plt.plot(g.p, g.y, "o-", label=name)
    m = max(0.4, float(max(np.max(p) for p in preds.values())))
    plt.plot([0, m], [0, m], "k:", lw=1)
    plt.xlabel("Predicted risk"); plt.ylabel("Observed risk")
    plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(path, dpi=150); plt.close()


def plot_decision_curve(preds, y, path, tmax=0.4):
    th = np.linspace(0.02, tmax, 60)
    plt.figure(figsize=(5.5, 5))
    for name, p in preds.items():
        plt.plot(th, net_benefit(y, p, th), label=name)
    prev = np.mean(y)
    plt.plot(th, prev - (1 - prev) * th / (1 - th), "--", label="treat all")
    plt.axhline(0, color="k", lw=1, label="treat none")
    plt.ylim(-0.03, prev + 0.02)
    plt.xlabel("Threshold risk"); plt.ylabel("Net benefit")
    plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(path, dpi=150); plt.close()
