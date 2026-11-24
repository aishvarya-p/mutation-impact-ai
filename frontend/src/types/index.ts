export interface VariantInput {
  chromosome: string;
  position: number;
  reference_allele: string;
  alternate_allele: string;
  gene_symbol: string;
  variant_type?: string;
  hgvs_name?: string;
}

export interface BiologicalFeatures {
  chrom_num: number;
  relative_position: number;
  is_snv: boolean;
  mutation_mechanism: string;
  is_cpg_island_transition: boolean;
  molecular_consequence: string;
  grantham_distance: number;
  charge_change: number;
  polarity_change: number;
  gene_pathogenicity_propensity: number;
}

export interface ExternalAnnotation {
  gene_symbol: string;
  gene_description?: string;
  ncbi_gene_id?: string;
  ensembl_id?: string;
  chromosome_location?: string;
  source: string;
  status: string;
}

export interface PredictionResponse {
  classification: 'Benign' | 'Pathogenic';
  probability_benign: number;
  probability_pathogenic: number;
  confidence_score: number;
  risk_level: 'Low' | 'Moderate' | 'High' | 'Critical';
  submitted_variant: {
    chromosome: string;
    position: number;
    reference_allele: string;
    alternate_allele: string;
    gene_symbol: string;
    variant_type?: string;
    hgvs_name?: string;
  };
  biological_features: BiologicalFeatures;
  external_annotation?: ExternalAnnotation;
  explanation: string;
  scientific_disclaimer: string;
  model_version: string;
}

export interface ModelMetrics {
  cv_accuracy_mean: number;
  cv_accuracy_std: number;
  cv_f1_mean: number;
  cv_roc_mean: number;
  test_accuracy: number;
  test_precision: number;
  test_recall: number;
  test_specificity: number;
  test_f1: number;
  test_roc_auc: number;
  confusion_matrix: {
    tn: number;
    fp: number;
    fn: number;
    tp: number;
  };
}

export interface ModelInfoResponse {
  selected_model: string;
  model_architecture: string;
  classes: string[];
  training_samples: number;
  testing_samples: number;
  metrics: Record<string, ModelMetrics>;
  feature_importances: Record<string, number>;
  available_figures: string[];
}

export interface DatasetSummaryResponse {
  total_variants: number;
  benign_variants: number;
  pathogenic_variants: number;
  unique_genes: number;
  chromosomes_represented: string[];
  variant_types: Record<string, number>;
  top_10_genes: Record<string, number>;
}

export interface HealthResponse {
  status: string;
  service_name: string;
  version: string;
  model_loaded: boolean;
  selected_model?: string;
}
