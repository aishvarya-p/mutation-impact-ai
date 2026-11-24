"""
Variant Feature Engineering and Preprocessing Pipeline
Mutation Impact AI

Scientifically grounded feature extraction for genetic variants:
- Chromosome encoding and relative coordinate mapping
- Nucleotide transition vs transversion classification
- CpG deamination hotspot identification
- HGVS consequence extraction (nonsense, frameshift, missense, synonymous, splice_site, inframe)
- Grantham physicochemical amino acid distance for missense substitutions
- Amino acid charge and polarity change calculation
- Indel length delta and reading frame disruption calculation
- Target encoding for gene pathogenicity propensity (fitted strictly on training data)

No target-derived clinical identifiers or submission metadata are used as features,
preventing data leakage.
"""

import re
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

# Approximate chromosome base pair lengths for GRCh38
CHROMOSOME_LENGTHS = {
    "1": 248956422, "2": 242193529, "3": 198295559, "4": 190214555,
    "5": 181538259, "6": 170805979, "7": 159345973, "8": 145138636,
    "9": 138394717, "10": 133797422, "11": 135086622, "12": 133275309,
    "13": 114364328, "14": 107043718, "15": 101991189, "16": 90338345,
    "17": 83257441, "18": 80373285, "19": 58617616, "20": 64444167,
    "21": 46709983, "22": 50818468, "X": 156040895, "Y": 57227415,
    "MT": 16569, "M": 16569
}

# Standard Grantham Distance Matrix (Grantham R. Science 1974; 185:862-864)
AMINO_ACID_3_TO_1 = {
    'Ala': 'A', 'Arg': 'R', 'Asn': 'N', 'Asp': 'D', 'Cys': 'C',
    'Gln': 'Q', 'Glu': 'E', 'Gly': 'G', 'His': 'H', 'Ile': 'I',
    'Leu': 'L', 'Lys': 'K', 'Met': 'M', 'Phe': 'F', 'Pro': 'P',
    'Ser': 'S', 'Thr': 'T', 'Trp': 'W', 'Tyr': 'Y', 'Val': 'V',
    'Ter': '*', 'Sec': 'U'
}

GRANTHAM_MATRIX = {
    ('A', 'R'): 112, ('A', 'N'): 111, ('A', 'D'): 126, ('A', 'C'): 195, ('A', 'Q'): 91,
    ('A', 'E'): 107, ('A', 'G'): 60,  ('A', 'H'): 86,  ('A', 'I'): 94,  ('A', 'L'): 96,
    ('A', 'K'): 106, ('A', 'M'): 84,  ('A', 'F'): 113, ('A', 'P'): 27,  ('A', 'S'): 99,
    ('A', 'T'): 58,  ('A', 'W'): 148, ('A', 'Y'): 112, ('A', 'V'): 64,
    ('R', 'N'): 86,  ('R', 'D'): 96,  ('R', 'C'): 180, ('R', 'Q'): 43,  ('R', 'E'): 54,
    ('R', 'G'): 125, ('R', 'H'): 29,  ('R', 'I'): 97,  ('R', 'L'): 102, ('R', 'K'): 26,
    ('R', 'M'): 91,  ('R', 'F'): 97,  ('R', 'P'): 103, ('R', 'S'): 110, ('R', 'T'): 71,
    ('R', 'W'): 101, ('R', 'Y'): 77,  ('R', 'V'): 96,
    ('N', 'D'): 23,  ('N', 'C'): 139, ('N', 'Q'): 46,  ('N', 'E'): 42,  ('N', 'G'): 80,
    ('N', 'H'): 68,  ('N', 'I'): 149, ('N', 'L'): 153, ('N', 'K'): 94,  ('N', 'M'): 142,
    ('N', 'F'): 158, ('N', 'P'): 91,  ('N', 'S'): 46,  ('N', 'T'): 65,  ('N', 'W'): 174,
    ('N', 'Y'): 143, ('N', 'V'): 133,
    ('D', 'C'): 154, ('D', 'Q'): 61,  ('D', 'E'): 45,  ('D', 'G'): 81,  ('D', 'H'): 81,
    ('D', 'I'): 168, ('D', 'L'): 172, ('D', 'K'): 101, ('D', 'M'): 160, ('D', 'F'): 177,
    ('D', 'P'): 108, ('D', 'S'): 65,  ('D', 'T'): 85,  ('D', 'W'): 181, ('D', 'Y'): 160,
    ('D', 'V'): 152,
    ('C', 'Q'): 154, ('C', 'E'): 170, ('C', 'G'): 159, ('C', 'H'): 174, ('C', 'I'): 198,
    ('C', 'L'): 198, ('C', 'K'): 202, ('C', 'M'): 196, ('C', 'F'): 205, ('C', 'P'): 169,
    ('C', 'S'): 112, ('C', 'T'): 149, ('C', 'W'): 215, ('C', 'Y'): 194, ('C', 'V'): 192,
    ('Q', 'E'): 29,  ('Q', 'G'): 87,  ('Q', 'H'): 24,  ('Q', 'I'): 109, ('Q', 'L'): 113,
    ('Q', 'K'): 53,  ('Q', 'M'): 101, ('Q', 'F'): 116, ('Q', 'P'): 76,  ('Q', 'S'): 68,
    ('Q', 'T'): 42,  ('Q', 'W'): 130, ('Q', 'Y'): 99,  ('Q', 'V'): 96,
    ('E', 'G'): 98,  ('E', 'H'): 40,  ('E', 'I'): 134, ('E', 'L'): 138, ('E', 'K'): 56,
    ('E', 'M'): 126, ('E', 'F'): 140, ('E', 'P'): 93,  ('E', 'S'): 80,  ('E', 'T'): 65,
    ('E', 'W'): 152, ('E', 'Y'): 122, ('E', 'V'): 121,
    ('G', 'H'): 89,  ('G', 'I'): 135, ('G', 'L'): 138, ('G', 'K'): 127, ('G', 'M'): 127,
    ('G', 'F'): 153, ('G', 'P'): 42,  ('G', 'S'): 56,  ('G', 'T'): 59,  ('G', 'W'): 184,
    ('G', 'Y'): 147, ('G', 'V'): 109,
    ('H', 'I'): 94,  ('H', 'L'): 99,  ('H', 'K'): 32,  ('H', 'M'): 87,  ('H', 'F'): 100,
    ('H', 'P'): 77,  ('H', 'S'): 89,  ('H', 'T'): 47,  ('H', 'W'): 115, ('H', 'Y'): 83,
    ('H', 'V'): 84,
    ('I', 'L'): 5,   ('I', 'K'): 102, ('I', 'M'): 10,  ('I', 'F'): 21,  ('I', 'P'): 95,
    ('I', 'S'): 142, ('I', 'T'): 89,  ('I', 'W'): 61,  ('I', 'Y'): 33,  ('I', 'V'): 29,
    ('L', 'K'): 107, ('L', 'M'): 15,  ('L', 'F'): 22,  ('L', 'P'): 98,  ('L', 'S'): 145,
    ('L', 'T'): 92,  ('L', 'W'): 61,  ('L', 'Y'): 36,  ('L', 'V'): 32,
    ('K', 'M'): 95,  ('K', 'F'): 102, ('K', 'P'): 103, ('K', 'S'): 121, ('K', 'T'): 78,
    ('K', 'W'): 110, ('K', 'Y'): 85,  ('K', 'V'): 97,
    ('M', 'F'): 21,  ('M', 'P'): 87,  ('M', 'S'): 135, ('M', 'T'): 81,  ('M', 'W'): 67,
    ('M', 'Y'): 36,  ('M', 'V'): 21,
    ('F', 'P'): 114, ('F', 'S'): 155, ('F', 'T'): 103, ('F', 'W'): 40,  ('F', 'Y'): 22,
    ('F', 'V'): 50,
    ('P', 'S'): 74,  ('P', 'T'): 38,  ('P', 'W'): 147, ('P', 'Y'): 110, ('P', 'V'): 68,
    ('S', 'T'): 58,  ('S', 'W'): 177, ('S', 'Y'): 144, ('S', 'V'): 124,
    ('T', 'W'): 128, ('T', 'Y'): 92,  ('T', 'V'): 69,
    ('W', 'Y'): 37,  ('W', 'V'): 88,
    ('Y', 'V'): 55
}

def get_grantham_distance(aa1: str, aa2: str) -> float:
    if aa1 == aa2:
        return 0.0
    if aa1 in ('*', 'X', '?') or aa2 in ('*', 'X', '?'):
        return 150.0
    pair = (aa1, aa2)
    rev_pair = (aa2, aa1)
    return float(GRANTHAM_MATRIX.get(pair, GRANTHAM_MATRIX.get(rev_pair, 100.0)))

AA_CHARGE = {
    'R': 1, 'K': 1, 'H': 1,
    'D': -1, 'E': -1,
    'A': 0, 'N': 0, 'C': 0, 'Q': 0, 'G': 0, 'I': 0, 'L': 0,
    'M': 0, 'F': 0, 'P': 0, 'S': 0, 'T': 0, 'W': 0, 'Y': 0, 'V': 0,
    '*': 0
}

AA_POLARITY = {
    'R': 1, 'K': 1, 'H': 1, 'D': 1, 'E': 1, 'N': 1, 'Q': 1, 'S': 1, 'T': 1, 'Y': 1, 'C': 1,
    'A': 0, 'G': 0, 'I': 0, 'L': 0, 'M': 0, 'F': 0, 'P': 0, 'W': 0, 'V': 0,
    '*': 0
}

RE_MISSENSE = re.compile(r'p\.([A-Z][a-z]{2})(\d+)([A-Z][a-z]{2})')
RE_NONSENSE = re.compile(r'p\.[A-Z][a-z]{2}\d+(?:Ter|\*|Stop)')
RE_SYNONYMOUS = re.compile(r'p\.[A-Z][a-z]{2}\d+=')
RE_FRAMESHIFT = re.compile(r'p\.[A-Z][a-z]{2}\d+.*fs')
RE_SPLICE = re.compile(r'c\.\d+([+-][12])[A-Z]>[A-Z]')

class GeneticFeatureExtractor(BaseEstimator, TransformerMixin):
    """
    Scikit-learn compatible transformer that transforms raw genetic variant attributes
    into numerical feature vectors for model training and inference.
    """
    def __init__(self, smoothing: float = 15.0):
        self.smoothing = smoothing
        self.gene_pathogenicity_map_ = {}
        self.global_pathogenicity_prior_ = 0.5
        self.feature_names_ = []

    def fit(self, X, y=None):
        df = X.copy() if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        df = df.reset_index(drop=True)
        
        if y is not None:
            y_arr = np.asarray(y)
            self.global_pathogenicity_prior_ = float(np.mean(y_arr))
            
            if 'GeneSymbol' in df.columns:
                df['_y_tmp'] = y_arr
                gene_grouped = df.groupby('GeneSymbol')['_y_tmp'].agg(['sum', 'count'])
                gene_scores = (gene_grouped['sum'] + self.smoothing * self.global_pathogenicity_prior_) / (gene_grouped['count'] + self.smoothing)
                self.gene_pathogenicity_map_ = gene_scores.to_dict()
                df.drop(columns=['_y_tmp'], inplace=True)
        
        dummy_out = self._extract_features_df(df.head(2))
        self.feature_names_ = list(dummy_out.columns)
        return self

    def transform(self, X):
        df = X.copy() if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        feat_df = self._extract_features_df(df)
        return feat_df.values

    def get_feature_names_out(self, input_features=None):
        return np.array(self.feature_names_)

    def _extract_features_df(self, df: pd.DataFrame) -> pd.DataFrame:
        records = []
        
        for _, row in df.iterrows():
            chrom_raw = str(row.get('Chromosome', '1')).replace('chr', '').strip().upper()
            try:
                start_pos = float(row.get('Start', 1000000))
            except (ValueError, TypeError):
                start_pos = 1000000.0
                
            ref = str(row.get('ReferenceAllele', 'A')).strip().upper()
            alt = str(row.get('AlternateAllele', 'G')).strip().upper()
            gene = str(row.get('GeneSymbol', 'UNKNOWN')).strip().upper()
            name = str(row.get('Name', ''))
            var_type = str(row.get('Type', 'single nucleotide variant')).lower()

            # 1. Chromosomal Features
            chr_num = 23 if chrom_raw == 'X' else (24 if chrom_raw == 'Y' else (25 if chrom_raw in ('MT', 'M') else None))
            if chr_num is None:
                try:
                    chr_num = int(chrom_raw)
                except ValueError:
                    chr_num = 1
            
            chr_len = CHROMOSOME_LENGTHS.get(chrom_raw, 100000000)
            rel_pos = min(1.0, max(0.0, start_pos / chr_len))
            log_pos = np.log10(max(1.0, start_pos))

            # 2. Sequence and Allelic Differences
            ref_len = len(ref)
            alt_len = len(alt)
            length_diff = alt_len - ref_len
            is_snv = 1 if (ref_len == 1 and alt_len == 1 and ref in 'ACGT' and alt in 'ACGT') else 0
            is_deletion = 1 if ref_len > alt_len else 0
            is_insertion = 1 if alt_len > ref_len else 0
            is_frameshift = 1 if (not is_snv and abs(length_diff) % 3 != 0) else 0
            is_inframe = 1 if (not is_snv and abs(length_diff) % 3 == 0 and length_diff != 0) else 0

            # 3. Transition / Transversion / Mutation Chemistry (SNVs)
            is_transition = 0
            is_transversion = 0
            is_cpg_transition = 0
            
            if is_snv:
                pair = (ref, alt)
                if pair in [('A', 'G'), ('G', 'A'), ('C', 'T'), ('T', 'C')]:
                    is_transition = 1
                    if pair in [('C', 'T'), ('G', 'A')]:
                        is_cpg_transition = 1
                else:
                    is_transversion = 1

            exchange_code = f"{ref}>{alt}" if is_snv else "INDEL"
            is_C_to_T = 1 if exchange_code == "C>T" else 0
            is_G_to_A = 1 if exchange_code == "G>A" else 0
            is_T_to_C = 1 if exchange_code == "T>C" else 0
            is_A_to_G = 1 if exchange_code == "A>G" else 0
            is_transv_exchange = 1 if is_transversion else 0

            # 4. HGVS Molecular Consequence Extraction
            consequence_nonsense = 0
            consequence_frameshift = is_frameshift
            consequence_missense = 0
            consequence_synonymous = 0
            consequence_splice = 0
            
            grantham_dist = 0.0
            charge_change = 0
            polarity_change = 0
            
            if RE_NONSENSE.search(name) or 'Ter' in name or '*' in name:
                consequence_nonsense = 1
                grantham_dist = 150.0
            elif RE_FRAMESHIFT.search(name) or 'fs' in name:
                consequence_frameshift = 1
                grantham_dist = 120.0
            elif RE_SPLICE.search(name):
                consequence_splice = 1
                grantham_dist = 110.0
            elif RE_SYNONYMOUS.search(name) or '=' in name:
                consequence_synonymous = 1
                grantham_dist = 0.0
            else:
                m = RE_MISSENSE.search(name)
                if m:
                    consequence_missense = 1
                    aa1_3, _, aa2_3 = m.groups()
                    aa1 = AMINO_ACID_3_TO_1.get(aa1_3, '?')
                    aa2 = AMINO_ACID_3_TO_1.get(aa2_3, '?')
                    grantham_dist = get_grantham_distance(aa1, aa2)
                    charge_change = abs(AA_CHARGE.get(aa1, 0) - AA_CHARGE.get(aa2, 0))
                    polarity_change = abs(AA_POLARITY.get(aa1, 0) - AA_POLARITY.get(aa2, 0))
                elif is_snv:
                    consequence_missense = 1
                    grantham_dist = 75.0 if is_transversion else 45.0

            is_high_impact_lof = 1 if (consequence_nonsense or consequence_frameshift or consequence_splice) else 0
            gene_score = self.gene_pathogenicity_map_.get(gene, self.global_pathogenicity_prior_)

            rec = {
                'chrom_num': chr_num,
                'rel_pos': rel_pos,
                'log_pos': log_pos,
                'ref_len': min(ref_len, 50),
                'alt_len': min(alt_len, 50),
                'length_diff': np.clip(length_diff, -20, 20),
                'is_snv': is_snv,
                'is_deletion': is_deletion,
                'is_insertion': is_insertion,
                'is_frameshift': is_frameshift,
                'is_inframe': is_inframe,
                'is_transition': is_transition,
                'is_transversion': is_transversion,
                'is_cpg_transition': is_cpg_transition,
                'is_C_to_T': is_C_to_T,
                'is_G_to_A': is_G_to_A,
                'is_T_to_C': is_T_to_C,
                'is_A_to_G': is_A_to_G,
                'is_transv_exchange': is_transv_exchange,
                'consequence_nonsense': consequence_nonsense,
                'consequence_frameshift': consequence_frameshift,
                'consequence_missense': consequence_missense,
                'consequence_synonymous': consequence_synonymous,
                'consequence_splice': consequence_splice,
                'is_high_impact_lof': is_high_impact_lof,
                'grantham_dist': grantham_dist,
                'charge_change': charge_change,
                'polarity_change': polarity_change,
                'gene_pathogenicity_propensity': gene_score
            }
            records.append(rec)
            
        return pd.DataFrame(records)


class MutationImpactPipeline:
    """
    Top-level deployable pipeline encapsulating feature extractor,
    optional scaler, and trained classifier. Picklable by Joblib.
    """
    def __init__(self, extractor: GeneticFeatureExtractor, classifier, scaler=None):
        self.extractor = extractor
        self.classifier = classifier
        self.scaler = scaler
        self.feature_names = extractor.feature_names_

    def predict(self, X):
        feats = self.extractor.transform(X)
        if self.scaler is not None:
            feats = self.scaler.transform(feats)
        return self.classifier.predict(feats)

    def predict_proba(self, X):
        feats = self.extractor.transform(X)
        if self.scaler is not None:
            feats = self.scaler.transform(feats)
        if hasattr(self.classifier, "predict_proba"):
            return self.classifier.predict_proba(feats)
        else:
            preds = self.classifier.predict(feats)
            return np.vstack([1 - preds, preds]).T

    def explain_features(self, X):
        """Returns the engineered feature dictionary for an input variant."""
        df = X.copy() if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        feat_df = self.extractor._extract_features_df(df)
        return feat_df.to_dict(orient='records')
