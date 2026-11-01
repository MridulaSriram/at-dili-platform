"""
End-to-end run. Usage:

    python run_demo.py                      # synthetic cohort (code check only)
    python run_demo.py --data my_cohort.csv # your real data

Outputs go to ./results
"""
import argparse
import os
import numpy as np
import pandas as pd

import config as C
import evaluate as E
import train_validate as T
from genotypes import GENETIC_FEATURES
from score_model import LiteratureScore, summarize_score, risk_tier
from simulate_cohort import simulate

OUT = "results"


def main(path=None):
    os.makedirs(OUT, exist_ok=True)
    if path:
        df = pd.read_csv(path)
        print(f"Loaded {path}: {len(df)} rows")
    else:
        df = simulate()
        df.to_csv(f"{OUT}/simulated_cohort.csv", index=False)
        print("USING SIMULATED DATA. Numbers below do not describe real patients.")

    X, y, region = T.prepare(df)
    print(f"n = {len(y)}, cases = {y.sum()} ({y.mean():.1%})")
    if y.sum() < 100:
        print("WARNING: fewer than 100 cases. Estimates will be unstable.")

    # 1. Fixed literature score -------------------------------------------
    lit = LiteratureScore()
    lit.calibrate_intercept(X[GENETIC_FEATURES])
    summarize_score(lit).to_csv(f"{OUT}/literature_terms.csv", index=False)
    p_lit = lit.predict_proba(X[GENETIC_FEATURES].fillna(0))
    print(f"\nLiterature score intercept: {lit.intercept:.3f}")

    # 2. Data-driven models, out-of-fold --------------------------------
    preds = {"literature score": p_lit}
    rows = [E.summary_row("literature score (no fitting)", y, p_lit)]
    for name, builder in T.model_zoo(X).items():
        p = T.oof_predictions(X, y, builder)
        preds[name] = p
        rows.append(E.summary_row(name, y, p))
    table = pd.DataFrame(rows).round(3)
    table.to_csv(f"{OUT}/model_comparison.csv", index=False)
    print("\nModel comparison (cross-validated):")
    print(table[["model", "AUC", "AUC_lo", "AUC_hi", "Brier",
                 "calib_slope", "mean_pred", "observed"]].to_string(index=False))

    # 3. Optimism-corrected AUC for the main combined model -------------
    comb = T.model_zoo(X)["combined (L2)"]
    app, corr = T.bootstrap_optimism(X, y, comb, n_boot=200)
    print(f"\nCombined (L2) AUC: apparent {app:.3f}, optimism-corrected {corr:.3f}")

    # 4. Leave-one-region-out ----------------------------------------------
    loro_c = T.leave_one_region_out(X, y, region, comb)
    loro_l = T.leave_one_region_out(X, y, region, literature=True)
    loro = loro_c.merge(loro_l, on=["held_out", "n", "cases", "observed"],
                        suffixes=("_combined", "_literature"))
    loro.round(3).to_csv(f"{OUT}/leave_one_region_out.csv", index=False)
    print("\nLeave-one-region-out AUC:")
    print(loro[["held_out", "n", "cases", "AUC_combined", "AUC_literature"]]
          .round(3).to_string(index=False))

    # 5. Odds ratios ----------------------------------------------------------
    cols = GENETIC_FEATURES + T.CLINICAL_FEATURES
    ors, n_used, n_cases = T.odds_ratio_table(X, y, cols)
    ors.round(3).to_csv(f"{OUT}/odds_ratios.csv")
    print(f"\nUnpenalised odds ratios (n={n_used}, cases={n_cases}):")
    print(ors.round(3).to_string())
    expl = [c for c in C.OPTIONAL_EXPLORATORY_COLS if c in X.columns]
    if expl:
        o2, _, _ = T.odds_ratio_table(X, y, cols + expl)
        print("\nExploratory PPAR terms (adjusted):")
        print(o2.loc[expl].round(3).to_string())

    # 6. Risk tiers --------------------------------------------------------------
    tiers = pd.Series(risk_tier(p_lit)).value_counts()
    obs = pd.Series(y).groupby(risk_tier(p_lit)).mean()
    print("\nLiterature-score tiers (n, observed AT-DILI rate):")
    for t in ["low", "moderate", "high"]:
        if t in tiers:
            print(f"  {t:9s} n={tiers[t]:5d}  observed {obs[t]:.1%}")

    # 7. Plots -----------------------------------------------------------------
    show = {k: preds[k] for k in ["literature score", "clinical only",
                                  "genetic only", "combined (L2)"]}
    E.plot_roc(show, y, f"{OUT}/roc.png")
    E.plot_calibration(show, y, f"{OUT}/calibration.png")
    E.plot_decision_curve(show, y, f"{OUT}/decision_curve.png")
    print(f"\nTables and plots saved in ./{OUT}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", help="CSV with the columns in config.py")
    main(ap.parse_args().data)
