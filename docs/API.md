# Mutation Impact AI — REST API Documentation

**FastAPI High-Performance Inference Endpoints**

Interactive Swagger Documentation is served live at: `http://localhost:8000/docs`

---

## 1. Primary Inference Endpoint

### `POST /predict` (and `POST /api/predict`)

Predicts the functional clinical impact (Benign vs Pathogenic) for a single human genetic variant.

#### Request Body (`application/json`)

```json
{
  "chromosome": "17",
  "position": 7673802,
  "reference_allele": "C",
  "alternate_allele": "T",
  "gene_symbol": "TP53",
  "variant_type": "single nucleotide variant",
  "hgvs_name": "NM_000546.5(TP53):c.844C>T (p.Arg282Trp)"
}
```

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `chromosome` | string | Yes | Chromosome identifier (1–22, X, Y, MT). Case-insensitive, accepts `chr` prefix. |
| `position` | integer | Yes | Genomic start coordinate (GRCh38 assembly, $> 0$). |
| `reference_allele` | string | Yes | Wild-type nucleotide sequence (e.g. `C`). |
| `alternate_allele` | string | Yes | Mutant nucleotide sequence (e.g. `T`). |
| `gene_symbol` | string | No | HGNC official gene symbol (e.g. `TP53`). |
| `variant_type` | string | No | `single nucleotide variant`, `deletion`, `insertion`, or `indel`. |
| `hgvs_name` | string | No | HGVS nomenclature string used to extract codon and amino acid change. |

#### Response (`200 OK`)

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
  "external_annotation": {
    "gene_symbol": "TP53",
    "gene_description": "Tumor protein p53; cellular tumor antigen and sequence-specific DNA-binding transcription factor.",
    "ncbi_gene_id": "7157",
    "ensembl_id": "ENSG00000141510",
    "chromosome_location": "17p13.1",
    "source": "Ensembl REST API (Live)",
    "status": "Verified"
  },
  "explanation": "The genetic variant chr17:7673802 (C>T) in gene TP53 is classified as Pathogenic with an estimated model probability of 90.1% Pathogenic vs 9.9% Benign. The missense substitution yields a Grantham physicochemical distance of 101. A Grantham score exceeding 100 indicates substantial stereochemical and polarity divergence, suggesting destabilizing structural impact on protein folding. The mutation occurs at a classic CpG deamination locus (C>T / G>A transition), a known human mutational hotspot.",
  "scientific_disclaimer": "This application provides research-oriented machine learning predictions based on its training data. Predictions are not medical diagnoses and should not be used for clinical decision-making.",
  "model_version": "Random Forest v1.0.0"
}
```

---

## 2. Batch Inference Endpoint

### `POST /api/predict/batch`

Evaluates up to 100 genetic variants in a single API call.

#### Request Body

```json
{
  "variants": [
    {
      "chromosome": "17",
      "position": 7673802,
      "reference_allele": "C",
      "alternate_allele": "T",
      "gene_symbol": "TP53"
    },
    {
      "chromosome": "7",
      "position": 117175400,
      "reference_allele": "A",
      "alternate_allele": "G",
      "gene_symbol": "CFTR",
      "hgvs_name": "NM_000492.3:c.1584G>A (p.Glu528=)"
    }
  ]
}
```

---

## 3. System & Health Endpoints

### `GET /health`

Returns operational health and model memory residency.

```json
{
  "status": "healthy",
  "service_name": "Mutation Impact AI",
  "version": "1.0.0",
  "model_loaded": true,
  "selected_model": "Random Forest"
}
```

### `GET /`

Returns root project metadata, version, and links to documentation.

---

## 4. Model Metadata & Figure Endpoints

### `GET /api/model/info`

Returns architecture details, 5-model comparative metrics, training/testing sample counts, and feature importances.

### `GET /api/model/figures/{filename}`

Streams publication-grade PNG evaluation figures generated during training:
- `confusion_matrix.png`
- `roc_curve.png`
- `precision_recall_curve.png`
- `feature_importance.png`
- `model_comparison.png`

### `GET /api/dataset/summary`

Returns authentic dataset counts, top genes, and chromosome representations.
