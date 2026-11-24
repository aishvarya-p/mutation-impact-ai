"""
Variant Prediction Service
Mutation Impact AI - Backend

Executes real-time inference using the loaded Scikit-learn Random Forest pipeline,
extracts biological feature attributes, formats clinical risk levels,
and builds clear scientific explanations.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

from backend.app.core.config import settings
from backend.app.core.model_loader import model_manager
from backend.app.api.schemas import (
    VariantInput,
    PredictionResponse,
    BiologicalFeatures,
    ExternalAnnotation
)
from backend.app.services.external_bio import fetch_external_gene_annotation

async def predict_variant_impact(variant: VariantInput) -> PredictionResponse:
    if not model_manager.is_loaded or model_manager.pipeline is None:
        raise RuntimeError("Machine learning model is not loaded in backend memory.")
        
    # Build single-row DataFrame for pipeline input
    input_data = pd.DataFrame([{
        "Chromosome": str(variant.chromosome),
        "Start": int(variant.position),
        "ReferenceAllele": str(variant.reference_allele),
        "AlternateAllele": str(variant.alternate_allele),
        "GeneSymbol": str(variant.gene_symbol),
        "Type": str(variant.variant_type or "single nucleotide variant"),
        "Name": str(variant.hgvs_name or "")
    }])
    
    # 1. Run inference
    pipeline = model_manager.pipeline
    pred_class_idx = int(pipeline.predict(input_data)[0])
    probabilities = pipeline.predict_proba(input_data)[0]
    
    prob_benign = float(np.round(probabilities[0], 4))
    prob_pathogenic = float(np.round(probabilities[1], 4))
    
    classification = "Pathogenic" if pred_class_idx == 1 else "Benign"
    confidence = float(np.round(max(prob_benign, prob_pathogenic), 4))
    
    # 2. Extract engineered biological features
    feat_dicts = pipeline.explain_features(input_data)
    f = feat_dicts[0]
    
    # Mechanism string
    if f.get("is_snv", 0) == 1:
        if f.get("is_cpg_transition", 0) == 1:
            mechanism = "CpG Transition (Spontaneous Deamination Hotspot)"
        elif f.get("is_transition", 0) == 1:
            mechanism = "Purine/Pyrimidine Transition"
        else:
            mechanism = "Transversion (Purine <-> Pyrimidine)"
    elif f.get("is_frameshift", 0) == 1:
        mechanism = "Frameshifting Indel"
    elif f.get("is_inframe", 0) == 1:
        mechanism = "In-frame Indel"
    elif f.get("is_deletion", 0) == 1:
        mechanism = "Genomic Deletion"
    elif f.get("is_insertion", 0) == 1:
        mechanism = "Genomic Insertion"
    else:
        mechanism = "Complex Indel"
        
    # Consequence string
    if f.get("consequence_nonsense", 0) == 1:
        consequence_str = "Nonsense / Stop-Gain (Truncating)"
    elif f.get("consequence_frameshift", 0) == 1:
        consequence_str = "Frameshift Disruption"
    elif f.get("consequence_splice", 0) == 1:
        consequence_str = "Canonical Splice Junction Disruption"
    elif f.get("consequence_synonymous", 0) == 1:
        consequence_str = "Synonymous Silent Substitution"
    elif f.get("consequence_missense", 0) == 1:
        consequence_str = "Missense Amino Acid Substitution"
    else:
        consequence_str = "Genomic Sequence Variant"
        
    bio_features = BiologicalFeatures(
        chrom_num=int(f.get("chrom_num", 1)),
        relative_position=float(np.round(f.get("rel_pos", 0.0), 4)),
        is_snv=bool(f.get("is_snv", 1)),
        mutation_mechanism=mechanism,
        is_cpg_island_transition=bool(f.get("is_cpg_transition", 0)),
        molecular_consequence=consequence_str,
        grantham_distance=float(f.get("grantham_dist", 0.0)),
        charge_change=int(f.get("charge_change", 0)),
        polarity_change=int(f.get("polarity_change", 0)),
        gene_pathogenicity_propensity=float(np.round(f.get("gene_pathogenicity_propensity", 0.5), 4))
    )
    
    # 3. Clinical Risk Level assignment
    if classification == "Pathogenic":
        risk_level = "Critical" if prob_pathogenic >= 0.85 else "High"
    else:
        risk_level = "Low" if prob_benign >= 0.80 else "Moderate"
        
    # 4. Scientific Explanation Generation
    explanation_parts = []
    explanation_parts.append(
        f"The genetic variant chr{variant.chromosome}:{variant.position} ({variant.reference_allele}>{variant.alternate_allele}) "
        f"in gene {variant.gene_symbol} is classified as {classification} with an estimated model probability of {prob_pathogenic*100:.1f}% Pathogenic vs {prob_benign*100:.1f}% Benign."
    )
    
    if f.get("is_high_impact_lof", 0) == 1:
        explanation_parts.append(
            "This mutation generates a high-impact loss-of-function effect (premature termination codon, frameshift, or splice donor/acceptor disruption), "
            "which strongly elevates pathogenicity likelihood according to ACMG/AMP PVS1 criteria."
        )
    elif f.get("consequence_synonymous", 0) == 1:
        explanation_parts.append(
            "This variant represents a synonymous substitution preserving the primary amino acid sequence, "
            "consistent with typical benign clinical presentation (ACMG BP7 criteria)."
        )
    elif f.get("consequence_missense", 0) == 1:
        gd = f.get("grantham_dist", 0.0)
        explanation_parts.append(
            f"The missense substitution yields a Grantham physicochemical distance of {gd:.0f}."
        )
        if gd > 100:
            explanation_parts.append(
                "A Grantham score exceeding 100 indicates substantial stereochemical and polarity divergence, suggesting destabilizing structural impact on protein folding."
            )
        else:
            explanation_parts.append(
                "A moderate or low Grantham score indicates relatively conservative physicochemical properties between the reference and mutant residues."
            )
            
    if f.get("is_cpg_transition", 0) == 1:
        explanation_parts.append(
            "The mutation occurs at a classic CpG deamination locus (C>T / G>A transition), a known human mutational hotspot."
        )
        
    gene_score = f.get("gene_pathogenicity_propensity", 0.5)
    if gene_score > 0.65:
        explanation_parts.append(
            f"Gene {variant.gene_symbol} exhibits high clinical constraint and disease-association density in ClinVar (smoothed pathogenicity propensity: {gene_score:.2f})."
        )
    elif gene_score < 0.35:
        explanation_parts.append(
            f"Gene {variant.gene_symbol} exhibits established polymorphic tolerance in benchmark datasets (smoothed pathogenicity propensity: {gene_score:.2f})."
        )
        
    explanation = " ".join(explanation_parts)
    
    # 5. External Biological Annotation Lookup
    external_annot = await fetch_external_gene_annotation(variant.gene_symbol)
    
    # 6. Submitted Variant payload
    submitted_dict = {
        "chromosome": str(variant.chromosome),
        "position": variant.position,
        "reference_allele": variant.reference_allele,
        "alternate_allele": variant.alternate_allele,
        "gene_symbol": variant.gene_symbol,
        "variant_type": variant.variant_type,
        "hgvs_name": variant.hgvs_name
    }
    
    return PredictionResponse(
        classification=classification,
        probability_benign=prob_benign,
        probability_pathogenic=prob_pathogenic,
        confidence_score=confidence,
        risk_level=risk_level,
        submitted_variant=submitted_dict,
        biological_features=bio_features,
        external_annotation=external_annot,
        explanation=explanation,
        scientific_disclaimer=settings.SCIENTIFIC_DISCLAIMER,
        model_version=f"{model_manager.metrics.get('selected_model', 'Random Forest')} v{settings.VERSION}"
    )
