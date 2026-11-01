"""
Central settings for the AT-DILI multi-gene risk score project.

Everything marked PLACEHOLDER must be replaced with real values before any
result is treated as evidence. The effect sizes come from the published
estimates you collected (see evidence_table.csv). The allele frequencies and
clinical effects are NOT from your data. They only let the demo run.
"""
import numpy as np

# ---------------------------------------------------------------------------
# 1. Literature effect sizes used by the fixed (literature) score
#    OR with 95% CI. beta = ln(OR). se = (ln(hi) - ln(lo)) / (2 * 1.96)
# ---------------------------------------------------------------------------
EVIDENCE = {
    "nat2_slow":   dict(or_=3.30, lo=2.65, hi=4.11,
                        label="NAT2 slow acetylator (2 slow alleles) vs other"),
    "cyp2e1_c1c1": dict(or_=1.39, lo=1.06, hi=1.83,
                        label="CYP2E1 RsaI/PstI c1/c1 vs c2 carrier"),
    "gstm1_null":  dict(or_=1.30, lo=1.12, hi=1.52,
                        label="GSTM1 null (deletion)"),
    "gstt1_null":  dict(or_=1.83, lo=1.01, hi=3.55,
                        label="GSTT1 null (deletion), single study"),
}

def beta_se(name):
    e = EVIDENCE[name]
    beta = float(np.log(e["or_"]))
    se = float((np.log(e["hi"]) - np.log(e["lo"])) / (2 * 1.96))
    return beta, se

# ---------------------------------------------------------------------------
# 2. Baseline incidence of AT-DILI in India (used to anchor the intercept)
#    12.6% = pooled estimate for four first-line drugs in an Indian review.
#    Replace with the figure from your own cohort or a newer meta-analysis.
# ---------------------------------------------------------------------------
BASELINE_RISK = 0.126

# Risk tiers on the absolute-risk scale. ARBITRARY until a decision-curve
# analysis or a clinical consensus fixes real thresholds.
TIER_LOW_BELOW = 0.10
TIER_HIGH_AT_OR_ABOVE = 0.20

# ---------------------------------------------------------------------------
# 3. PLACEHOLDER population genetics for the simulation only
#    NAT2 is simulated by haplotype: *4 (rapid/wild type), *5, *6, *7.
#    Region labels are examples. Replace with your real sites.
# ---------------------------------------------------------------------------
REGIONS = ["North", "South", "East", "West", "Northeast"]
REGION_WEIGHTS = [0.30, 0.25, 0.15, 0.20, 0.10]

NAT2_HAP_FREQ = {   # region -> (*4, *5, *6, *7)  must each sum to 1
    "North":     (0.28, 0.33, 0.35, 0.04),
    "South":     (0.38, 0.32, 0.26, 0.04),
    "East":      (0.35, 0.34, 0.27, 0.04),
    "West":      (0.30, 0.38, 0.28, 0.04),
    "Northeast": (0.42, 0.28, 0.26, 0.04),
}
# rs2031920 T = c2 allele. 1000 Genomes South Asian is ~1%, but Indian
# PCR-RFLP studies report far more c2 carriers. VERIFY with GenomeIndia/gnomAD.
CYP2E1_C2_FREQ = 0.10
GSTM1_NULL_FREQ = {"North": 0.30, "South": 0.38, "East": 0.35,
                   "West": 0.32, "Northeast": 0.45}
GSTT1_NULL_FREQ = {"North": 0.20, "South": 0.25, "East": 0.22,
                   "West": 0.22, "Northeast": 0.30}
PPARA_ALT_FREQ = 0.25   # exploratory SNP, simulated with NO true effect
PPARG_ALT_FREQ = 0.12   # exploratory SNP, simulated with NO true effect

# ILLUSTRATIVE clinical effects (odds ratios). These are assumptions, not
# evidence. They exist only so the clinical-only and combined models differ.
CLINICAL_OR = {
    "age_per_10y": 1.15, "female": 1.35, "alcohol": 1.6, "hiv": 1.8,
    "albumin_per_gdl": 0.70, "bmi_below_18_5": 1.4,
}

# In the simulation the true NAT2 effect is scaled per region so you can see
# what regional heterogeneity does to a fixed score (the Indian studies
# disagree). 1.0 means the literature effect holds fully in that region.
SIM_NAT2_EFFECT_SCALE = {"North": 0.6, "South": 1.0, "East": 1.0,
                         "West": 1.1, "Northeast": 0.9}

# ---------------------------------------------------------------------------
# 4. Column names expected in a real data file
# ---------------------------------------------------------------------------
GENOTYPE_INPUT_COLS = [
    "nat2_rs1801280",    # NAT2*5, c.341T>C, copies of C: 0/1/2
    "nat2_rs1799930",    # NAT2*6, c.590G>A, copies of A: 0/1/2
    "nat2_rs1799931",    # NAT2*7, c.857G>A, copies of A: 0/1/2
    "cyp2e1_rs2031920",  # copies of T (the c2 allele): 0/1/2
    "gstm1_null",        # 1 = deleted on both chromosomes, 0 = present
    "gstt1_null",        # 1 = deleted on both chromosomes, 0 = present
]
OPTIONAL_EXPLORATORY_COLS = ["ppara_snp", "pparg_snp"]   # copies 0/1/2
CLINICAL_COLS = ["age", "female", "alcohol", "hiv", "albumin", "bmi"]
OUTCOME_COL = "atdili"      # 1 = AT-DILI by your fixed definition, 0 = no
REGION_COL = "region"

RANDOM_SEED = 2026
