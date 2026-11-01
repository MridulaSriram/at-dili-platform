"""
Fit data-driven models and judge them honestly.

Input: a table with the columns listed in config.py (one row per patient).
Steps:
  1. encode genotypes into 4 features (genotypes.py)
  2. compare clinical-only, genetic-only, combined and fixed-literature models
  3. out-of-fold predictions from repeated stratified cross-validation
  4. bootstrap optimism correction for the combined model
  5. leave-one-region-out validation (does it transfer between regions?)
  6. unpenalised odds ratios with 95% CI for the report
"""
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import config as C
warnings.filterwarnings("ignore", category=FutureWarning)
from genotypes import (encode_features, add_clinical_features,
                       GENETIC_FEATURES, CLINICAL_FEATURES)
from score_model import LiteratureScore


# ------------------------------------------------------------------ data
def prepare(df):
    """Return X (all features), y, region."""
    need = C.CLINICAL_COLS + [C.OUTCOME_COL, C.REGION_COL]
    miss = [c for c in need if c not in df.columns]
    if miss:
        raise ValueError(f"Missing columns: {miss}")
    G = encode_features(df)
    K = add_clinical_features(df)
    X = pd.concat([G, K], axis=1)
    for c in C.OPTIONAL_EXPLORATORY_COLS:
        if c in df.columns:
            X[c] = df[c].astype(float)
    return X, df[C.OUTCOME_COL].astype(int).to_numpy(), df[C.REGION_COL].to_numpy()


# ---------------------------------------------------------------- models
def make_lr(cols, penalty="l2", Cval=1.0):
    kw = dict(max_iter=5000)
    if penalty == "elasticnet":
        kw.update(penalty="elasticnet", l1_ratio=0.5, solver="saga")
    else:
        kw.update(solver="lbfgs")
    return Pipeline([
        ("prep", ColumnTransformer([("num", Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("sc", StandardScaler())]), cols)])),
        ("clf", LogisticRegression(C=Cval, **kw))])


def make_gbm(cols):
    return Pipeline([
        ("prep", ColumnTransformer([("num", SimpleImputer(strategy="median"), cols)])),
        ("clf", HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05,
                                               max_iter=150, random_state=C.RANDOM_SEED))])


def model_zoo(X):
    expl = [c for c in C.OPTIONAL_EXPLORATORY_COLS if c in X.columns]
    comb = GENETIC_FEATURES + CLINICAL_FEATURES
    zoo = {
        "clinical only": lambda: make_lr(CLINICAL_FEATURES),
        "genetic only": lambda: make_lr(GENETIC_FEATURES),
        "combined (L2)": lambda: make_lr(comb),
        "combined (elastic net)": lambda: make_lr(comb, "elasticnet", 0.5),
        "combined + PPAR (elastic net)": lambda: make_lr(comb + expl, "elasticnet", 0.5),
        "combined (boosted trees)": lambda: make_gbm(comb),
    }
    if not expl:
        zoo.pop("combined + PPAR (elastic net)")
    return zoo


# ------------------------------------------------------ cross-validation
def oof_predictions(X, y, builder, n_splits=5, n_repeats=3):
    """Average out-of-fold prediction over repeated stratified K-fold."""
    cv = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats,
                                 random_state=C.RANDOM_SEED)
    s = np.zeros(len(y)); k = np.zeros(len(y))
    for tr, te in cv.split(X, y):
        m = builder().fit(X.iloc[tr], y[tr])
        s[te] += m.predict_proba(X.iloc[te])[:, 1]; k[te] += 1
    return s / k


def bootstrap_optimism(X, y, builder, n_boot=200, seed=C.RANDOM_SEED):
    """
    Harrell optimism correction for AUC.
    corrected = apparent AUC - mean(AUC on bootstrap sample - AUC on original).
    """
    rng = np.random.default_rng(seed)
    full = builder().fit(X, y)
    apparent = roc_auc_score(y, full.predict_proba(X)[:, 1])
    opt = []
    for _ in range(n_boot):
        i = rng.integers(0, len(y), len(y))
        if y[i].min() == y[i].max():
            continue
        m = builder().fit(X.iloc[i], y[i])
        a_boot = roc_auc_score(y[i], m.predict_proba(X.iloc[i])[:, 1])
        a_orig = roc_auc_score(y, m.predict_proba(X)[:, 1])
        opt.append(a_boot - a_orig)
    return apparent, apparent - float(np.mean(opt))


def leave_one_region_out(X, y, region, builder=None, literature=False):
    """
    Train on all regions but one, test on the left-out region. For the fixed
    literature score nothing is trained, but the intercept is re-calibrated on
    the training regions only, to mimic deploying it elsewhere.
    """
    rows = []
    for r in sorted(set(region)):
        te = region == r; tr = ~te
        if literature:
            lit = LiteratureScore()
            lit.calibrate_intercept(X.loc[tr, GENETIC_FEATURES])
            p = lit.predict_proba(X.loc[te, GENETIC_FEATURES])
        else:
            m = builder().fit(X.loc[tr], y[tr])
            p = m.predict_proba(X.loc[te])[:, 1]
        if y[te].min() == y[te].max():
            continue
        rows.append(dict(held_out=r, n=int(te.sum()), cases=int(y[te].sum()),
                         AUC=roc_auc_score(y[te], p),
                         mean_pred=float(np.mean(p)), observed=float(np.mean(y[te]))))
    return pd.DataFrame(rows)


# ------------------------------------------------- odds ratio reporting
def odds_ratio_table(X, y, cols):
    """Unpenalised logistic regression with 95% CI (complete cases only)."""
    D = X[cols].copy(); D["y"] = y
    D = D.dropna()
    fit = sm.Logit(D["y"], sm.add_constant(D[cols])).fit(disp=0)
    ci = fit.conf_int()
    out = pd.DataFrame({"OR": np.exp(fit.params), "CI_low": np.exp(ci[0]),
                        "CI_high": np.exp(ci[1]), "p": fit.pvalues})
    return out.drop(index="const"), int(len(D)), int(D["y"].sum())
