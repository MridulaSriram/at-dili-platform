
"""
AT-DILI Demonstration API

This API serves predictions from a model trained entirely
on synthetic data.

It is for software demonstration only.
It is NOT clinically validated and must not be used for
real patient risk assessment or medical decisions.
"""

import json
from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict


# --------------------------------------------------
# Load model and metadata
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "artifacts"

MODEL_PATH = MODEL_DIR / "atdili_demo_model.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        "Model file not found. Run export_model.py first."
    )

if not METADATA_PATH.exists():
    raise FileNotFoundError(
        "Model metadata not found. Run export_model.py first."
    )

model = joblib.load(MODEL_PATH)

with open(METADATA_PATH, "r", encoding="utf-8") as file:
    metadata = json.load(file)

FEATURES = metadata["features"]


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="AT-DILI Demonstration API",
    description=(
        "An educational API using a model trained on synthetic data. "
        "Its outputs are not medical risk estimates."
    ),
    version="1.0.0"
)


# --------------------------------------------------
# CORS configuration
# --------------------------------------------------

# Local development origins.
# Port 5176 is included because Vite selected it
# when the earlier development ports were occupied.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# --------------------------------------------------
# Input validation
# --------------------------------------------------

class PredictionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Genetic features
    nat2_slow: int = Field(ge=0, le=1)
    cyp2e1_c1c1: int = Field(ge=0, le=1)
    gstm1_null: int = Field(ge=0, le=1)
    gstt1_null: int = Field(ge=0, le=1)

    # Clinical demonstration features
    age: float = Field(ge=15, le=80)
    female: int = Field(ge=0, le=1)
    alcohol: int = Field(ge=0, le=1)
    hiv: int = Field(ge=0, le=1)
    albumin: float = Field(ge=1.8, le=5.0)
    bmi: float = Field(ge=12, le=35)


# --------------------------------------------------
# Convert input to model features
# --------------------------------------------------

def prepare_input(data: PredictionInput):

    values = data.model_dump()

    # Apply the same feature transformations used during training.
    values["age10"] = (values["age"] - 40) / 10
    values["bmi_low"] = int(values["bmi"] < 18.5)

    model_values = {
        "nat2_slow": values["nat2_slow"],
        "cyp2e1_c1c1": values["cyp2e1_c1c1"],
        "gstm1_null": values["gstm1_null"],
        "gstt1_null": values["gstt1_null"],
        "age10": values["age10"],
        "female": values["female"],
        "alcohol": values["alcohol"],
        "hiv": values["hiv"],
        "albumin": values["albumin"],
        "bmi_low": values["bmi_low"],
    }

    return pd.DataFrame(
        [model_values],
        columns=FEATURES
    )


# --------------------------------------------------
# Health endpoint
# --------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "ok",
        "model_loaded": True,
        "model_name": metadata["model_name"],
        "training_data": metadata["training_data"],
        "clinical_validation": False,
        "message": "Synthetic demonstration API is running."
    }


# --------------------------------------------------
# Prediction endpoint
# --------------------------------------------------

@app.post("/demo/predict")
def predict(data: PredictionInput):

    try:
        X = prepare_input(data)

        probability = float(model.predict_proba(X)[0, 1])

        return {
            "success": True,
            "demo_only": True,
            "probability": round(probability, 4),
            "percentage": round(probability * 100, 2),
            "model_name": metadata["model_name"],
            "clinical_validation": False,
            "disclaimer": metadata["disclaimer"]
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(error)}"
        )
