"""
API Route Definitions
Mutation Impact AI - Backend
"""

import os
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import FileResponse

from backend.app.core.config import settings
from backend.app.core.model_loader import model_manager
from backend.app.api.schemas import (
    VariantInput,
    VariantBatchInput,
    PredictionResponse,
    BatchPredictionResponse,
    HealthResponse,
    ModelInfoResponse,
    DatasetSummaryResponse,
    ExternalAnnotation
)
from backend.app.services.prediction_service import predict_variant_impact
from backend.app.services.external_bio import fetch_external_gene_annotation

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["System"])
async def get_health():
    """Health check endpoint confirming service status and model memory residency."""
    return HealthResponse(
        status="healthy" if model_manager.is_loaded else "degraded",
        service_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        model_loaded=model_manager.is_loaded,
        selected_model=model_manager.metrics.get("selected_model", "Unknown")
    )

@router.post("/predict", response_model=PredictionResponse, tags=["Inference"])
async def predict_variant(variant: VariantInput):
    """
    Main Prediction Endpoint.
    Predicts clinical functional impact (Benign vs Pathogenic) for a single genetic variant.
    """
    try:
        return await predict_variant_impact(variant)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference execution error: {str(e)}")

@router.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Inference"])
async def predict_batch_variants(batch: VariantBatchInput):
    """Batch inference endpoint for evaluating up to 100 genetic variants in a single call."""
    results = []
    for var in batch.variants:
        res = await predict_variant_impact(var)
        results.append(res)
    return BatchPredictionResponse(
        total_processed=len(results),
        predictions=results
    )

@router.get("/model/info", response_model=ModelInfoResponse, tags=["Model"])
async def get_model_info():
    """Returns actual trained model architecture, evaluation metrics, and feature importances."""
    if not model_manager.is_loaded:
        raise HTTPException(status_code=503, detail="Model artifacts not yet loaded.")
        
    metrics_data = model_manager.metrics
    metadata_data = model_manager.metadata
    
    # Check available figures
    available_figs = []
    if os.path.exists(settings.FIGURES_DIR):
        available_figs = [f for f in os.listdir(settings.FIGURES_DIR) if f.endswith(".png")]
        
    return ModelInfoResponse(
        selected_model=metrics_data.get("selected_model", "Random Forest"),
        model_architecture=metadata_data.get("model_architecture", "Random Forest Classifier"),
        classes=metadata_data.get("classes", ["Benign", "Pathogenic"]),
        training_samples=metrics_data.get("training_samples", 16000),
        testing_samples=metrics_data.get("testing_samples", 4000),
        metrics=metrics_data.get("models_evaluated", {}),
        feature_importances=metadata_data.get("feature_importances", {}),
        available_figures=available_figs
    )

@router.get("/model/figures/{filename}", tags=["Model"])
async def get_figure(filename: str = Path(..., description="Figure filename (e.g. confusion_matrix.png)")):
    """Streams publication-grade scientific evaluation figures."""
    safe_filename = os.path.basename(filename)
    fig_path = os.path.join(settings.FIGURES_DIR, safe_filename)
    if not os.path.exists(fig_path):
        raise HTTPException(status_code=404, detail=f"Figure '{safe_filename}' not found.")
    return FileResponse(fig_path, media_type="image/png")

@router.get("/dataset/summary", response_model=DatasetSummaryResponse, tags=["Dataset"])
async def get_dataset_summary():
    """Returns dataset summary statistics derived from the authentic ClinVar GRCh38 extract."""
    if not model_manager.dataset_summary:
        raise HTTPException(status_code=404, detail="Dataset summary not found.")
    return DatasetSummaryResponse(**model_manager.dataset_summary)

@router.get("/external/gene/{gene_symbol}", response_model=ExternalAnnotation, tags=["Biological Annotation"])
async def get_gene_details(gene_symbol: str):
    """Retrieves live biological annotations for a specified gene symbol."""
    return await fetch_external_gene_annotation(gene_symbol)
