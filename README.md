# Mutation Impact AI
### AI-Based Prediction of Functional Impact of SNPs and Genetic Mutations

[![Python](https://img.shields.io/badge/Python-3.14%20%7C%203.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![ClinVar](https://img.shields.io/badge/Dataset-NCBI%20ClinVar%20GRCh38-2E7D32?style=flat-square)](https://www.ncbi.nlm.nih.gov/clinvar/)
[![License](https://img.shields.io/badge/License-MIT-slate?style=flat-square)](LICENSE)

---

## 1. Executive Summary

**Mutation Impact AI** is an autonomous, full-stack computational genomics application engineered to classify human genetic mutations and single nucleotide polymorphisms (SNPs) into **Benign** or **Pathogenic** clinical impact categories.

Designed as a biotechnology research product, it replaces generic heuristics with a rigorous machine learning pipeline trained on **20,000 verified peer-reviewed records from the official NCBI ClinVar repository** (GRCh38 assembly). The platform incorporates biochemical and evolutionary signals—including the **Grantham amino acid distance matrix**, **Loss-of-Function (LoF) transcript consequences**, **CpG deamination hotspots**, and **empirical Bayes gene constraint priors**—with zero target data leakage.

```
                      +---------------------------------------+
                      |   Genomic Coordinates & Alleles      |
                      |   chr17:7673802 C>T (TP53 Arg282Trp)  |
                      +-------------------+-------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|               GeneticFeatureExtractor (29 Biological Predictors)                  |
|  * Grantham Chemical Distance (101.0)      * CpG Transition Deamination (C>T)    |
|  * Molecular Consequence (Missense)        * Gene Pathogenicity Propensity (0.57) |
|  * Indel Framing & Length Delta            * Relative Chromosomal Coordinate     |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                    Random Forest Classifier (150 Estimators)                     |
|           Test Accuracy: 90.48%  |  Pathogenic Recall (Sensitivity): 92.55%       |
|           ROC-AUC Score: 0.9705  |  5-Fold Stratified Cross-Validation: 92.07%     |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
                      +-------------------+-------------------+
                      |   Clinical Impact Classification      |
                      |   Pathogenic (90.1% Confidence)       |
                      |   Risk Tier: Critical • Ensembl Annot |
                      +---------------------------------------+
```

---

## 2. Verified Benchmark Performance

All models were evaluated on an identical, strictly held-out test split of **4,000 variants** (2,000 Benign, 2,000 Pathogenic) following 5-Fold Stratified Cross-Validation on the 16,000-variant training set:

| Model Architecture | 5-Fold CV Acc (±std) | Test Accuracy | Precision | Pathogenic Recall | Specificity | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest (Selected)** | **0.9207 ± 0.007** | **90.48%** | **88.86%** | **92.55%** | **88.40%** | **0.9067** | **0.9705** |
| **HistGradientBoosting** | 0.9246 ± 0.005 | 90.65% | 89.70% | 91.85% | 89.45% | 0.9076 | 0.9708 |
| **Decision Tree** | 0.9101 ± 0.007 | 89.80% | 88.38% | 91.65% | 87.95% | 0.8999 | 0.9435 |
| **K-Nearest Neighbors** | 0.8991 ± 0.007 | 89.70% | 88.17% | 91.70% | 87.70% | 0.8990 | 0.9550 |
| **Logistic Regression** | 0.9062 ± 0.005 | 89.12% | 87.60% | 91.15% | 87.10% | 0.8934 | 0.9594 |

### Why Random Forest Was Selected
In clinical genetics, minimizing **False Negatives** (misclassifying a pathogenic mutation as benign) is critical to prevent diagnostic errors. Random Forest achieved the highest **Pathogenic Recall (92.55%)**, detecting 1,851 of 2,000 pathogenic mutations in the test set while maintaining strong overall accuracy (90.48%) and an ROC-AUC of 0.9705.

---

## 3. Key Features

- **Scientific UI/UX Design System:** Custom biotechnology aesthetic styled with deep scientific teal (`#063d34`), warm ivory backgrounds, charcoal typography, and restrained clinical outcome indicators.
- **29 Biologically Engineered Predictors:** Includes Grantham amino acid distance matrix, Loss-of-Function flags, transition/transversion dynamics, CpG hotspot deamination, and smoothed empirical Bayes gene constraint scores.
- **Zero Data Leakage:** Target clinical significance, submitter counts, and review annotations are strictly excluded from predictive features.
- **Production FastAPI Service:** Single-load in-memory model lifecycle (`@asynccontextmanager`), Pydantic validation, CORS middleware, and OpenAPI documentation (`/docs`).
- **Live External Annotations:** Ensembl REST API integration for human gene descriptions, coordinates, and Ensembl IDs with local graceful degradation.
- **Full Test Coverage:** 10 backend integration tests (`test_api.py`) and ML pipeline unit tests (`test_ml_pipeline.py`) verifying inference stability and validation boundaries.

---

## 4. Project Structure

```text
Mutation Projec/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entry point, CORS, static SPA mount
│   │   ├── api/routes.py               # Endpoints (/predict, /model/info, /health, etc.)
│   │   ├── api/schemas.py              # Pydantic validation schemas
│   │   ├── core/config.py              # Application settings
│   │   ├── core/model_loader.py        # ModelManager singleton
│   │   └── services/prediction_service.py # Core ML inference & explanation generator
│   ├── requirements.txt                # Python backend dependencies
│   └── tests/test_api.py               # 10 integration tests
├── data/
│   ├── raw/clinvar_raw_variants.tsv    # Raw authentic ClinVar extract (20,000 records)
│   └── processed/clinvar_cleaned.tsv   # Cleaned, standardized modeling dataset
├── docs/
│   ├── API.md                          # Complete REST API documentation
│   ├── ARCHITECTURE.md                 # System architecture & data flow
│   └── DATASET.md                      # ClinVar data provenance & feature dictionary
├── frontend/
│   ├── src/
│   │   ├── App.tsx                     # Primary layout & state management
│   │   ├── components/                 # Header & Footer components
│   │   ├── pages/                      # Dashboard, Predict, Performance, Dataset, About
│   │   ├── services/api.ts             # Typed REST API client
│   │   └── types/index.ts              # TypeScript interfaces
│   ├── dist/                           # Compiled production SPA assets
│   ├── package.json                    # Frontend dependencies
│   └── vite.config.ts                  # Vite build tool with backend proxying
├── ml/
│   ├── download_clinvar.py             # Reproducible streaming downloader
│   ├── preprocess.py                   # GeneticFeatureExtractor & pipeline
│   ├── train.py                        # Model training, 5-fold CV & figure generation
│   └── saved_models/
│       ├── mutation_impact_pipeline.joblib # Serialized model pipeline
│       ├── metrics.json                # Complete benchmark evaluation metrics
│       └── figures/                    # Publication-grade evaluation figures
└── tests/test_ml_pipeline.py           # Unit tests for preprocessing & inference
```

---

## 5. Installation & Setup

### Prerequisites
- **Python:** 3.10 or higher (Tested on Python 3.14)
- **Node.js:** 18.0 or higher (Tested on Node v24.17)
- **npm:** 9.0 or higher

### Step 1: Clone Repository & Install Python Dependencies
```bash
git clone https://github.com/your-username/mutation-impact-ai.git
cd mutation-impact-ai

pip install -r backend/requirements.txt
```

### Step 2: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 6. How to Run the Application

You can run the application in either **Development Mode** (with hot reload on both frontend and backend) or **Single-Command Unified Production Mode**.

### Option A: Unified Production Server (Single Command)
The FastAPI backend serves both the REST API and the compiled React SPA:

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
- Open browser at: **`http://127.0.0.1:8000/app`** (Interactive Full-Stack Web Application)
- Interactive API Documentation: **`http://127.0.0.1:8000/docs`**

### Option B: Development Mode (Hot-Reload)

**Terminal 1 — Backend Service:**
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — Frontend Dev Server:**
```bash
cd frontend
npm run dev
```
- Open browser at: **`http://localhost:5173`** (Vite automatically proxies API requests to port 8000)

---

## 7. Running the Test Suite

Execute the complete automated test suite covering machine learning pipelines and FastAPI endpoints:

```bash
# Run all tests
pytest backend/tests/test_api.py tests/test_ml_pipeline.py -v
```

**Test Verification Summary:**
- `test_root_endpoint`: Verifies system metadata and documentation links.
- `test_health_endpoint`: Verifies operational health and model memory residency.
- `test_predict_pathogenic_variant`: Tests inference on TP53 hotspot mutation (p.Arg282Trp).
- `test_predict_benign_synonymous_variant`: Tests inference on CFTR synonymous mutation (p.Glu528=).
- `test_predict_validation_error_chromosome`: Tests rejection of invalid human chromosomes (422).
- `test_predict_validation_error_nucleotide`: Tests rejection of invalid nucleotide characters (422).
- `test_get_model_info`: Validates metadata and figure availability.
- `test_get_dataset_summary`: Validates dataset records and gene breakdown.
- `test_get_figure`: Confirms streaming of publication PNG figures.
- `test_get_external_gene`: Verifies Ensembl REST API lookup and caching.
- `test_grantham_distances`: Validates chemical substitution matrix calculations.
- `test_feature_extractor_transform`: Validates 29-feature matrix extraction.

---

## 8. API Quickstart (cURL Example)

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "chromosome": "17",
       "position": 7673802,
       "reference_allele": "C",
       "alternate_allele": "T",
       "gene_symbol": "TP53",
       "variant_type": "single nucleotide variant",
       "hgvs_name": "NM_000546.5(TP53):c.844C>T (p.Arg282Trp)"
     }'
```

**Response:**
```json
{
  "classification": "Pathogenic",
  "probability_benign": 0.0993,
  "probability_pathogenic": 0.9007,
  "confidence_score": 0.9007,
  "risk_level": "Critical",
  "submitted_variant": {
    "chromosome": "17",
    "position": 7673802,
    "reference_allele": "C",
    "alternate_allele": "T",
    "gene_symbol": "TP53",
    "variant_type": "single nucleotide variant",
    "hgvs_name": "NM_000546.5(TP53):c.844C>T (p.Arg282Trp)"
  },
  "biological_features": {
    "chrom_num": 17,
    "relative_position": 0.0922,
    "is_snv": true,
    "mutation_mechanism": "CpG Transition (Spontaneous Deamination Hotspot)",
    "is_cpg_island_transition": true,
    "molecular_consequence": "Missense Amino Acid Substitution",
    "grantham_distance": 101.0,
    "charge_change": 1,
    "polarity_change": 1,
    "gene_pathogenicity_propensity": 0.5729
  },
  "explanation": "The genetic variant chr17:7673802 (C>T) in gene TP53 is classified as Pathogenic with an estimated model probability of 90.1% Pathogenic vs 9.9% Benign. The missense substitution yields a Grantham physicochemical distance of 101. A Grantham score exceeding 100 indicates substantial stereochemical and polarity divergence, suggesting destabilizing structural impact on protein folding. The mutation occurs at a classic CpG deamination locus (C>T / G>A transition), a known human mutational hotspot.",
  "scientific_disclaimer": "This application provides research-oriented machine learning predictions based on its training data. Predictions are not medical diagnoses and should not be used for clinical decision-making.",
  "model_version": "Random Forest v1.0.0"
}
```

---

## 9. Scientific Disclaimer & Ethical Guidelines

> **Mandatory Scientific Notice:** This application provides research-oriented machine learning predictions based on its training data. Predictions are not medical diagnoses and should not be used for clinical decision-making.

All clinical diagnostic classifications require validation in accredited molecular diagnostic laboratories (CLIA/CAP), comprehensive correlation with patient family history, population allele frequencies (gnomAD), segregation studies, and multi-disciplinary molecular tumor board review in accordance with ACMG/AMP consensus guidelines.

---

## 10. References & Citations

1. **Landrum MJ, et al.** (2020). ClinVar: improving access to variant interpretations and supporting evidence. *Nucleic Acids Research*, 48(D1):D835-D844.
2. **Richards S, et al.** (2015). Standards and guidelines for the interpretation of sequence variants: a joint consensus recommendation of the American College of Medical Genetics and Genomics and the Association for Molecular Pathology. *Genetics in Medicine*, 17(5):405-424.
3. **Grantham R.** (1974). Amino acid difference formula to help explain protein evolution. *Science*, 185(4154):862-864.
4. **Pedregosa F, et al.** (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12:2825-2830.
