"""
Configuration and Application Settings
Mutation Impact AI - Backend
"""

import os
from pydantic import BaseModel

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

class Settings(BaseModel):
    PROJECT_NAME: str = "Mutation Impact AI"
    PROJECT_TITLE: str = "AI-Based Prediction of Functional Impact of SNPs and Genetic Mutations"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Model Artifact Paths
    MODEL_PATH: str = os.path.join(PROJECT_ROOT, "ml", "saved_models", "mutation_impact_pipeline.joblib")
    METRICS_PATH: str = os.path.join(PROJECT_ROOT, "ml", "saved_models", "metrics.json")
    METADATA_PATH: str = os.path.join(PROJECT_ROOT, "ml", "saved_models", "model_metadata.json")
    FIGURES_DIR: str = os.path.join(PROJECT_ROOT, "ml", "saved_models", "figures")
    DATASET_SUMMARY_PATH: str = os.path.join(PROJECT_ROOT, "data", "processed", "dataset_summary.json")
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    SCIENTIFIC_DISCLAIMER: str = (
        "This application provides research-oriented machine learning predictions based on its training data. "
        "Predictions are not medical diagnoses and should not be used for clinical decision-making."
    )

settings = Settings()
