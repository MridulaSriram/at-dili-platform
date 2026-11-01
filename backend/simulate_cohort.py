"""
Make a synthetic TB cohort so you can test every step of the pipeline.

IMPORTANT: results on this data say nothing about real patients. The outcome is
generated from the same literature effects the fixed score uses, so the score
will look good by construction. The point of the simulation is to check that
the code runs, and to show how regional differences and small samples behave.
"""
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.special import expit
import config as C


def simulate(n=3000, seed=C.RANDOM_SEED, prevalence=C.BASELINE_RISK,
             nat2_scale=None):
    rng = np.random.default_rng(seed)
    nat2_scale = nat2_scale or C.SIM_NAT2_EFFECT_SCALE
    region = rng.choice(C.REGIONS, size=n, p=C.REGION_WEIGHTS)

    # NAT2 by haplotype: two chromosomes per person, labels *4,*5,*6,*7
    cnt = np.zeros((n, 4), dtype=int)
    for r in C.REGIONS:
        idx = np.where(region == r)[0]
        hap = rng.choice(4, size=(len(idx), 2), p=C.NAT2_HAP_FREQ[r])
        for k in range(4):
            cnt[idx, k] = (hap == k).sum(axis=1)

    df = pd.DataFrame({
        "region": region,
        "nat2_rs1801280": cnt[:, 1],     # copies of *5
        "nat2_rs1799930": cnt[:, 2],     # copies of *6
        "nat2_rs1799931": cnt[:, 3],     # copies of *7
        "cyp2e1_rs2031920": rng.binomial(2, C.CYP2E1_C2_FREQ, n),
        "ppara_snp": rng.binomial(2, C.PPARA_ALT_FREQ, n),
        "pparg_snp": rng.binomial(2, C.PPARG_ALT_FREQ, n),
    })
    df["gstm1_null"] = [rng.binomial(1, C.GSTM1_NULL_FREQ[r]) for r in region]
    df["gstt1_null"] = [rng.binomial(1, C.GSTT1_NULL_FREQ[r]) for r in region]

    # Clinical variables
    df["age"] = np.clip(rng.normal(40, 15, n), 15, 80).round()
    df["female"] = rng.binomial(1, 0.40, n)
    df["alcohol"] = rng.binomial(1, 0.20, n)
    df["hiv"] = rng.binomial(1, 0.05, n)
    df["albumin"] = np.clip(rng.normal(3.6, 0.6, n), 1.8, 5.0).round(1)
    df["bmi"] = np.clip(rng.normal(19.5, 3.5, n), 12, 35).round(1)

    # True log-odds
    slow = (np.minimum(df.nat2_rs1801280 + df.nat2_rs1799930
                       + df.nat2_rs1799931, 2) == 2).astype(float)
    c1c1 = (df.cyp2e1_rs2031920 == 0).astype(float)
    b = {k: C.beta_se(k)[0] for k in C.EVIDENCE}
    scale = df["region"].map(nat2_scale).to_numpy()
    lp = (b["nat2_slow"] * scale * slow + b["cyp2e1_c1c1"] * c1c1
          + b["gstm1_null"] * df.gstm1_null + b["gstt1_null"] * df.gstt1_null)
    co = C.CLINICAL_OR
    lp = lp + (np.log(co["age_per_10y"]) * (df.age - 40) / 10
               + np.log(co["female"]) * df.female
               + np.log(co["alcohol"]) * df.alcohol
               + np.log(co["hiv"]) * df.hiv
               + np.log(co["albumin_per_gdl"]) * (df.albumin - 3.6)
               + np.log(co["bmi_below_18_5"]) * (df.bmi < 18.5))
    lp = lp.to_numpy()   # PPARA/PPARG deliberately have NO effect

    b0 = brentq(lambda x: expit(x + lp).mean() - prevalence, -15, 5)
    df["atdili"] = rng.binomial(1, expit(b0 + lp))
    return df


if __name__ == "__main__":
    d = simulate()
    d.to_csv("results/simulated_cohort.csv", index=False)
    print(d.shape, "cases:", d.atdili.sum(), f"({d.atdili.mean():.1%})")
