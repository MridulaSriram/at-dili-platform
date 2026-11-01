"""
Fixed literature-based risk score.

logit(p) = b0 + sum( ln(OR_k) * feature_k )

The ORs come from config.EVIDENCE. Only the intercept b0 is calibrated, so that
the average predicted risk in a reference population equals the baseline
incidence. No patient outcome data are used, so this score is a starting point
and a benchmark, not a validated tool.
"""
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.special import expit, logit
import config as C
from genotypes import encode_features


class LiteratureScore:
    def __init__(self, baseline_risk=C.BASELINE_RISK):
        self.names = list(C.EVIDENCE.keys())
        self.beta = np.array([C.beta_se(n)[0] for n in self.names])
        self.se = np.array([C.beta_se(n)[1] for n in self.names])
        self.baseline_risk = baseline_risk
        self.intercept = None

    def _lp(self, X):
        return X[self.names].to_numpy(dtype=float) @ self.beta

    def calibrate_intercept(self, reference_features):
        """Find b0 so that mean predicted risk in the reference set = baseline."""
        lp = self._lp(reference_features.dropna(subset=self.names))
        f = lambda b0: expit(b0 + lp).mean() - self.baseline_risk
        self.intercept = brentq(f, -15, 5)
        return self.intercept

    def predict_proba(self, features):
        if self.intercept is None:
            raise RuntimeError("Call calibrate_intercept first.")
        return expit(self.intercept + self._lp(features))

    def predict_with_interval(self, features, n_draws=2000, seed=C.RANDOM_SEED):
        """
        Propagate the uncertainty in each log-OR (taken from its CI) by Monte
        Carlo. Gives a 95% interval around the predicted risk. It does NOT
        include uncertainty in the intercept or in model structure, so it is
        narrower than the true uncertainty.
        """
        rng = np.random.default_rng(seed)
        X = features[self.names].to_numpy(dtype=float)
        draws = rng.normal(self.beta, self.se, size=(n_draws, len(self.beta)))
        lp = X @ draws.T                                    # patients x draws
        p = expit(self.intercept + lp)
        return pd.DataFrame({"risk": self.predict_proba(features),
                             "lo": np.percentile(p, 2.5, axis=1),
                             "hi": np.percentile(p, 97.5, axis=1)},
                            index=features.index)

    def contributions(self, features_row):
        """Per-term contribution to the log-odds for one patient."""
        x = features_row[self.names].to_numpy(dtype=float)
        return pd.Series(x * self.beta, index=self.names)


def risk_tier(p):
    p = np.asarray(p)
    return np.where(p < C.TIER_LOW_BELOW, "low",
                    np.where(p >= C.TIER_HIGH_AT_OR_ABOVE, "high", "moderate"))


def summarize_score(model):
    rows = []
    for n, b, s in zip(model.names, model.beta, model.se):
        rows.append(dict(term=n, label=C.EVIDENCE[n]["label"],
                         OR=np.exp(b), beta=b, se=s))
    return pd.DataFrame(rows)
