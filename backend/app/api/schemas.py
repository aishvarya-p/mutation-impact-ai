"""
Pydantic Schemas and Request/Response Models
Mutation Impact AI - Backend
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

class VariantInput(BaseModel):
    chromosome: str = Field(..., description="Chromosome identifier (1-22, X, Y, MT)", examples=["17", "chr17"])
    position: int = Field(..., description="Genomic start coordinate (GRCh38)", gt=0, examples=[7673802])
    reference_allele: str = Field(..., description="Reference nucleotide sequence", min_length=1, examples=["C"])
    alternate_allele: str = Field(..., description="Alternate (mutant) nucleotide sequence", min_length=1, examples=["T"])
    gene_symbol: str = Field("UNKNOWN", description="HGNC Gene Symbol", examples=["TP53"])
    variant_type: Optional[str] = Field("single nucleotide variant", description="Variant classification type", examples=["single nucleotide variant", "deletion", "insertion", "indel"])
    hgvs_name: Optional[str] = Field(None, description="Optional HGVS notation nomenclature", examples=["NM_000546.5(TP53):c.844C>T (p.Arg282Trp)"])

    @field_validator("chromosome")
    @classmethod
    def clean_chromosome(cls, v: str) -> str:
        cleaned = v.replace("chr", "").strip().upper()
        valid = {str(i) for i in range(1, 23)}.union({"X", "Y", "MT", "M"})
        if cleaned not in valid:
            raise ValueError(f"Invalid chromosome '{v}'. Must be one of: 1-22, X, Y, MT.")
        return cleaned

    @field_validator("reference_allele", "alternate_allele")
    @classmethod
    def clean_allele(cls, v: str) -> str:
        cleaned = v.strip().upper()
        if not cleaned:
            raise ValueError("Allele sequence cannot be empty.")
        # Verify valid IUPAC nucleotide characters or deletion '-'
        for char in cleaned:
            if char not in "ACGTUN-":
                raise ValueError(f"Invalid nucleotide character '{char}' in allele sequence.")
        return cleaned

    @field_validator("gene_symbol")
    @classmethod
    def clean_gene(cls, v: str) -> str:
        return v.strip().upper() if v else "UNKNOWN"

class VariantBatchInput(BaseModel):
    variants: List[VariantInput] = Field(..., min_length=1, max_length=100)

class BiologicalFeatures(BaseModel):
    chrom_num: int
    relative_position: float
    is_snv: bool
    mutation_mechanism: str
    is_cpg_island_transition: bool
    molecular_consequence: str
    grantham_distance: float
    charge_change: int
    polarity_change: int
    gene_pathogenicity_propensity: float

class ExternalAnnotation(BaseModel):
    gene_symbol: str
    gene_description: Optional[str] = None
    ncbi_gene_id: Optional[str] = None
    ensembl_id: Optional[str] = None
    chromosome_location: Optional[str] = None
    source: str
    status: str

class PredictionResponse(BaseModel):
    classification: str = Field(..., description="Predicted clinical label: Benign or Pathogenic")
    probability_benign: float = Field(..., description="Estimated probability of Benign classification (0.0 to 1.0)")
    probability_pathogenic: float = Field(..., description="Estimated probability of Pathogenic classification (0.0 to 1.0)")
    confidence_score: float = Field(..., description="Confidence score of predicted class (0.5 to 1.0)")
    risk_level: str = Field(..., description="Clinical impact risk tier: Low, Moderate, High, or Critical")
    submitted_variant: Dict[str, Any]
    biological_features: BiologicalFeatures
    external_annotation: Optional[ExternalAnnotation] = None
    explanation: str
    scientific_disclaimer: str
    model_version: str

class BatchPredictionResponse(BaseModel):
    total_processed: int
    predictions: List[PredictionResponse]

class HealthResponse(BaseModel):
    status: str
    service_name: str
    version: str
    model_loaded: bool
    selected_model: Optional[str] = None

class ModelInfoResponse(BaseModel):
    selected_model: str
    model_architecture: str
    classes: List[str]
    training_samples: int
    testing_samples: int
    metrics: Dict[str, Any]
    feature_importances: Dict[str, float]
    available_figures: List[str]

class DatasetSummaryResponse(BaseModel):
    total_variants: int
    benign_variants: int
    pathogenic_variants: int
    unique_genes: int
    chromosomes_represented: List[str]
    variant_types: Dict[str, int]
    top_10_genes: Dict[str, int]
