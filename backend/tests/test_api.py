"""
Backend API Unit and Integration Tests
Mutation Impact AI
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.main import app
from backend.app.core.model_loader import model_manager

@pytest.fixture(scope="session", autouse=True)
def load_model_for_tests():
    """Ensure model artifacts are loaded in memory for the test session."""
    model_manager.load_artifacts()
    assert model_manager.is_loaded is True

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "Mutation Impact AI"
    assert data["status"] == "online"
    assert "disclaimer" in data

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert "selected_model" in data

def test_predict_pathogenic_variant(client):
    # TP53 hotspot mutation (p.Arg282Trp)
    payload = {
        "chromosome": "17",
        "position": 7673802,
        "reference_allele": "C",
        "alternate_allele": "T",
        "gene_symbol": "TP53",
        "variant_type": "single nucleotide variant",
        "hgvs_name": "NM_000546.5(TP53):c.844C>T (p.Arg282Trp)"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["classification"] in ["Benign", "Pathogenic"]
    assert "probability_benign" in data
    assert "probability_pathogenic" in data
    assert 0.0 <= data["probability_pathogenic"] <= 1.0
    assert data["risk_level"] in ["Low", "Moderate", "High", "Critical"]
    assert "biological_features" in data
    assert "explanation" in data
    assert "scientific_disclaimer" in data
    assert "Predictions are not medical diagnoses" in data["scientific_disclaimer"]

def test_predict_benign_synonymous_variant(client):
    # CFTR synonymous variant
    payload = {
        "chromosome": "7",
        "position": 117175400,
        "reference_allele": "A",
        "alternate_allele": "G",
        "gene_symbol": "CFTR",
        "variant_type": "single nucleotide variant",
        "hgvs_name": "NM_000492.3(CFTR):c.1584G>A (p.Glu528=)"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] == "Benign"
    assert data["probability_benign"] > 0.70
    assert data["biological_features"]["molecular_consequence"] == "Synonymous Silent Substitution"

def test_predict_validation_error_chromosome(client):
    payload = {
        "chromosome": "99",  # Invalid human chromosome
        "position": 1000,
        "reference_allele": "A",
        "alternate_allele": "T",
        "gene_symbol": "TEST"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_predict_validation_error_nucleotide(client):
    payload = {
        "chromosome": "1",
        "position": 1000,
        "reference_allele": "A",
        "alternate_allele": "Z",  # Invalid nucleotide
        "gene_symbol": "TEST"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_get_model_info(client):
    response = client.get("/api/model/info")
    assert response.status_code == 200
    data = response.json()
    assert "selected_model" in data
    assert "metrics" in data
    assert "feature_importances" in data
    assert len(data["available_figures"]) > 0

def test_get_dataset_summary(client):
    response = client.get("/api/dataset/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_variants"] == 20000
    assert data["benign_variants"] == 10000
    assert data["pathogenic_variants"] == 10000

def test_get_figure(client):
    response = client.get("/api/model/figures/confusion_matrix.png")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

def test_get_external_gene(client):
    response = client.get("/api/external/gene/TP53")
    assert response.status_code == 200
    data = response.json()
    assert data["gene_symbol"] == "TP53"
    assert "Tumor protein" in data["gene_description"] or "p53" in data["gene_description"]
