"""
Turn raw genotype columns into the four model features.

Why only four features: NAT2 has several correlated SNPs, CYP2E1 RsaI and PstI
are one haplotype, and the GST genes are deletions. Summing the odds ratio of
every SNP would count the same biology several times. So each gene gets ONE
feature.

    nat2_slow    1 if the person has 2 slow alleles (*5, *6 or *7), else 0
    cyp2e1_c1c1  1 if rs2031920 has no T allele (c1/c1), else 0
    gstm1_null   1 if GSTM1 is deleted on both chromosomes
    gstt1_null   1 if GSTT1 is deleted on both chromosomes
"""
import numpy as np
import pandas as pd
import config as C


def check_columns(df, cols):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")


def check_ranges(df):
    for c in ["nat2_rs1801280", "nat2_rs1799930", "nat2_rs1799931",
              "cyp2e1_rs2031920"]:
        bad = ~df[c].isin([0, 1, 2]) & df[c].notna()
        if bad.any():
            raise ValueError(f"{c} must be 0, 1 or 2 (copies of the variant allele)")
    for c in ["gstm1_null", "gstt1_null"]:
        bad = ~df[c].isin([0, 1]) & df[c].notna()
        if bad.any():
            raise ValueError(f"{c} must be 0 or 1")


def nat2_slow_allele_count(df):
    """
    Count slow alleles from the three defining SNPs. The data are unphased, so
    a person with variants at two loci might carry them on one chromosome
    (one slow allele) or on two (two slow alleles). NAT2*5, *6 and *7 sit on
    different haplotypes in almost everyone, so the sum is the usual choice.
    It is capped at 2 because a person only has two chromosomes.
    """
    total = df["nat2_rs1801280"] + df["nat2_rs1799930"] + df["nat2_rs1799931"]
    return total.clip(upper=2)


def nat2_class(df):
    n = nat2_slow_allele_count(df)
    return pd.Series(np.select([n == 0, n == 1], ["rapid", "intermediate"],
                               default="slow"), index=df.index)


def encode_features(df):
    """Return a DataFrame with the four genetic features. NaN stays NaN."""
    check_columns(df, C.GENOTYPE_INPUT_COLS)
    check_ranges(df)
    out = pd.DataFrame(index=df.index)
    n_slow = nat2_slow_allele_count(df)
    any_missing_nat2 = df[["nat2_rs1801280", "nat2_rs1799930",
                           "nat2_rs1799931"]].isna().any(axis=1)
    out["nat2_slow"] = (n_slow == 2).astype(float)
    out.loc[any_missing_nat2, "nat2_slow"] = np.nan

    out["cyp2e1_c1c1"] = (df["cyp2e1_rs2031920"] == 0).astype(float)
    out.loc[df["cyp2e1_rs2031920"].isna(), "cyp2e1_c1c1"] = np.nan

    out["gstm1_null"] = df["gstm1_null"].astype(float)
    out["gstt1_null"] = df["gstt1_null"].astype(float)
    return out


def add_clinical_features(df):
    """Add the derived clinical columns used by the data-driven models."""
    out = pd.DataFrame(index=df.index)
    out["age10"] = df["age"] / 10.0
    out["female"] = df["female"].astype(float)
    out["alcohol"] = df["alcohol"].astype(float)
    out["hiv"] = df["hiv"].astype(float)
    out["albumin"] = df["albumin"].astype(float)
    out["bmi_low"] = (df["bmi"] < 18.5).astype(float)
    out.loc[df["bmi"].isna(), "bmi_low"] = np.nan
    return out


GENETIC_FEATURES = ["nat2_slow", "cyp2e1_c1c1", "gstm1_null", "gstt1_null"]
CLINICAL_FEATURES = ["age10", "female", "alcohol", "hiv", "albumin", "bmi_low"]
