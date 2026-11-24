"""
Mutation Impact AI - FastAPI Application Entry Point
AI-Based Prediction of Functional Impact of SNPs and Genetic Mutations
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.core.config import settings
from backend.app.core.model_loader import model_manager
from backend.app.api.routes import router as api_router
from backend.app.api.schemas import (
    VariantInput,
    PredictionResponse,
    HealthResponse
)
from backend.app.services.prediction_service import predict_variant_impact
from starlette.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load ML model pipeline once into memory
    print(f"[*] Starting {settings.PROJECT_NAME} backend service...")
    try:
        model_manager.load_artifacts()
    except Exception as e:
        print(f"[!] Warning: Failed to pre-load model artifacts at startup: {e}")
    yield
    # Shutdown
    print(f"[*] Shutting down {settings.PROJECT_NAME} backend service...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Research API for predicting the functional clinical impact (Benign vs Pathogenic) "
        "of single nucleotide polymorphisms (SNPs) and genetic variants using genuine ClinVar data and machine learning."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Required Root Endpoint: GET /
@app.get("/", tags=["System"])
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "title": settings.PROJECT_TITLE,
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs",
        "health_check": "/health",
        "prediction_endpoint": "/predict",
        "disclaimer": settings.SCIENTIFIC_DISCLAIMER
    }

# 2. Required Health Endpoint: GET /health
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    return HealthResponse(
        status="healthy" if model_manager.is_loaded else "degraded",
        service_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        model_loaded=model_manager.is_loaded,
        selected_model=model_manager.metrics.get("selected_model", "Random Forest")
    )

# 3. Required Prediction Endpoint: POST /predict
@app.post("/predict", response_model=PredictionResponse, tags=["Inference"])
async def predict_variant_root(variant: VariantInput):
    """
    Direct root prediction endpoint.
    Accepts genetic variant coordinates and alleles, returns model prediction and biological features.
    """
    try:
        return await predict_variant_impact(variant)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference execution error: {str(e)}")

# Mount structured /api router
app.include_router(api_router, prefix=settings.API_PREFIX)

# Mount compiled production frontend if built
FRONTEND_DIST = os.path.join(PROJECT_ROOT, "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    app.mount("/app", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend_spa")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
