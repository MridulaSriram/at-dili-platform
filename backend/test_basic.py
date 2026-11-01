"""Quick checks. Run: python test_basic.py"""
import numpy as np
import pandas as pd
import config as C
from genotypes import encode_features, nat2_class
from score_model import LiteratureScore
from simulate_cohort import simulate


def row(**kw):
    base = dict(nat2_rs1801280=0, nat2_rs1799930=0, nat2_rs1799931=0,
                cyp2e1_rs2031920=1, gstm1_null=0, gstt1_null=0)
    base.update(kw)
    return pd.DataFrame([base])


def test_nat2_classes():
    assert nat2_class(row()).iloc[0] == "rapid"
    assert nat2_class(row(nat2_rs1801280=1)).iloc[0] == "intermediate"
    assert nat2_class(row(nat2_rs1801280=1, nat2_rs1799930=1)).iloc[0] == "slow"
    assert nat2_class(row(nat2_rs1799930=2)).iloc[0] == "slow"
    # cap at 2 slow alleles
    assert nat2_class(row(nat2_rs1801280=2, nat2_rs1799930=2)).iloc[0] == "slow"


def test_features():
    f = encode_features(row(cyp2e1_rs2031920=0, gstm1_null=1))
    assert f.cyp2e1_c1c1.iloc[0] == 1 and f.gstm1_null.iloc[0] == 1
    assert f.nat2_slow.iloc[0] == 0


def test_intercept_matches_baseline():
    F = encode_features(simulate(n=4000))
    m = LiteratureScore(); m.calibrate_intercept(F)
    assert abs(m.predict_proba(F).mean() - C.BASELINE_RISK) < 1e-4


def test_odds_ratio_recovered():
    F = encode_features(simulate(n=4000))
    m = LiteratureScore(); m.calibrate_intercept(F)
    a = F.copy(); b = F.copy(); a["nat2_slow"] = 1; b["nat2_slow"] = 0
    pa, pb = m.predict_proba(a)[0], m.predict_proba(b)[0]
    odds = lambda p: p / (1 - p)
    assert abs(odds(pa) / odds(pb) - 3.30) < 0.01


def test_bad_input_rejected():
    try:
        encode_features(row(nat2_rs1799930=3))
    except ValueError:
        return
    raise AssertionError("expected ValueError")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("ok", name)
