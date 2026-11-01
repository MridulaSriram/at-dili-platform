
"""
Train and export the AT-DILI synthetic demonstration model.

IMPORTANT:
This model is trained entirely on simulated data.
It is for software demonstration and testing only.
It is NOT clinically validated and must NOT be used for
real patient risk assessment or medical decisions.
"""

import json
from pathlib import Path
from datetime import datetime, timezone

import joblib
import sklearn

from simulate_cohort import simulate
from train_validate import prepare, model_zoo
from genotypes import GENETIC_FEATURES, CLINICAL_FEATURES


# --------------------------------------------------
# Configuration
# --------------------------------------------------

N_SAMPLES = 3000
RANDOM_SEED = 2026
MODEL_NAME = "combined (L2)"

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "artifacts"

MODEL_DIR.mkdir(exist_ok=True)

# Exactly 10 features used by Combined (L2)
MODEL_FEATURES = GENETIC_FEATURES + CLINICAL_FEATURES


# --------------------------------------------------
# Generate synthetic training data
# --------------------------------------------------

print("Generating synthetic cohort...")

df = simulate(n=N_SAMPLES, seed=RANDOM_SEED)

print(f"Generated records: {len(df)}")
print(f"Synthetic cases: {int(df['atdili'].sum())}")
print(f"Synthetic prevalence: {df['atdili'].mean():.2%}")


# --------------------------------------------------
# Prepare model features
# --------------------------------------------------

print("\nPreparing model features...")

X, y, region = prepare(df)

# Exclude optional exploratory PPARA and PPARG features
X_model = X[MODEL_FEATURES].copy()

print("Features used by the model:")
for feature in MODEL_FEATURES:
    print(f" - {feature}")

print(f"Total features: {len(MODEL_FEATURES)}")


# --------------------------------------------------
# Train Combined L2 model
# --------------------------------------------------

print("\nTraining Combined (L2) model...")

builders = model_zoo(X)

if MODEL_NAME not in builders:
    raise ValueError(f"Model not found: {MODEL_NAME}")

model = builders[MODEL_NAME]()
model.fit(X_model, y)

print("Model training completed.")


# --------------------------------------------------
# Save fitted model
# --------------------------------------------------

model_path = MODEL_DIR / "atdili_demo_model.joblib"

joblib.dump(model, model_path)

print(f"\nModel saved to: {model_path}")


# --------------------------------------------------
# Save model metadata
# --------------------------------------------------

metadata = {
    "model_name": MODEL_NAME,
    "model_type": "Logistic Regression with L2 regularisation",
    "purpose": "Synthetic software demonstration only",
    "clinical_validation": False,
    "training_data": "Simulated synthetic cohort",
    "training_records": int(len(df)),
    "synthetic_cases": int(y.sum()),
    "synthetic_prevalence": float(y.mean()),
    "random_seed": RANDOM_SEED,
    "features": list(MODEL_FEATURES),
    "feature_count": len(MODEL_FEATURES),
    "sklearn_version": sklearn.__version__,
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
    "disclaimer": (
        "Predictions are simulated demonstration outputs, "
        "not medical risk estimates. Do not use for clinical "
        "decisions or real patient assessment."
    )
}

metadata_path = MODEL_DIR / "model_metadata.json"

with open(metadata_path, "w", encoding="utf-8") as file:
    json.dump(metadata, file, indent=4)

print(f"Metadata saved to: {metadata_path}")


# --------------------------------------------------
# Test model prediction
# --------------------------------------------------

print("\nTesting exported model...")

sample = X_model.iloc[[0]]
probability = model.predict_proba(sample)[0, 1]

print(f"Example simulated probability: {probability:.4f}")
print("\nExport completed successfully!")
