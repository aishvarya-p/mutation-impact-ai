"""
Machine Learning Pipeline Unit Tests
Mutation Impact AI
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.preprocess import GeneticFeatureExtractor, MutationImpactPipeline, get_grantham_distance

def test_grantham_distances():
    # Identical amino acid has distance 0
    assert get_grantham_distance('L', 'L') == 0.0
    # Conservative substitution (Leu -> Ile is 5)
    assert get_grantham_distance('L', 'I') == 5.0
    assert get_grantham_distance('I', 'L') == 5.0
    # Radical substitution (Cys -> Trp is 215)
    assert get_grantham_distance('C', 'W') == 215.0
    # Stop codon substitution has penalty 150
    assert get_grantham_distance('R', '*') == 150.0

def test_feature_extractor_transform():
    extractor = GeneticFeatureExtractor(smoothing=10.0)
    
    sample_df = pd.DataFrame([
        {
            'Chromosome': 'chr17',
            'Start': 7673802,
            'ReferenceAllele': 'c',
            'AlternateAllele': 't',
            'GeneSymbol': 'TP53',
            'Name': 'NM_000546.5(TP53):c.844C>T (p.Arg282Trp)',
            'Type': 'single nucleotide variant'
        },
        {
            'Chromosome': '7',
            'Start': 117175400,
            'ReferenceAllele': 'A',
            'AlternateAllele': 'G',
            'GeneSymbol': 'CFTR',
            'Name': 'NM_000492.3(CFTR):c.1584G>A (p.Glu528=)',
            'Type': 'single nucleotide variant'
        }
    ])
    
    extractor.fit(sample_df, y=[1, 0])
    feats = extractor.transform(sample_df)
    
    assert feats.shape[0] == 2
    assert feats.shape[1] == 29
    
    feature_names = extractor.get_feature_names_out()
    assert 'grantham_dist' in feature_names
    assert 'gene_pathogenicity_propensity' in feature_names

def test_pipeline_inference_and_probabilities():
    model_path = os.path.join(PROJECT_ROOT, "ml", "saved_models", "mutation_impact_pipeline.joblib")
    assert os.path.exists(model_path)
    
    pipeline = joblib.load(model_path)
    
    sample_df = pd.DataFrame([{
        'Chromosome': '17',
        'Start': 7673802,
        'ReferenceAllele': 'C',
        'AlternateAllele': 'T',
        'GeneSymbol': 'TP53',
        'Name': 'NM_000546.5(TP53):c.844C>T (p.Arg282Trp)',
        'Type': 'single nucleotide variant'
    }])
    
    preds = pipeline.predict(sample_df)
    probs = pipeline.predict_proba(sample_df)
    
    assert len(preds) == 1
    assert preds[0] in [0, 1]
    assert probs.shape == (1, 2)
    assert np.isclose(probs[0].sum(), 1.0, atol=1e-4)
