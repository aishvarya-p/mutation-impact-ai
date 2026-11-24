import React, { useState, useEffect } from 'react';
import {
  Dna,
  Play,
  RotateCcw,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  ChevronRight,
  BookOpen
} from 'lucide-react';
import { VariantInput, PredictionResponse } from '../types';
import { predictVariant } from '../services/api';

interface PredictPageProps {
  initialVariant?: VariantInput;
}

export const PredictPage: React.FC<PredictPageProps> = ({ initialVariant }) => {
  const [formData, setFormData] = useState<VariantInput>({
    chromosome: '17',
    position: 7673802,
    reference_allele: 'C',
    alternate_allele: 'T',
    gene_symbol: 'TP53',
    variant_type: 'single nucleotide variant',
    hgvs_name: 'NM_000546.5(TP53):c.844C>T (p.Arg282Trp)',
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);

  useEffect(() => {
    if (initialVariant) {
      setFormData(initialVariant);
      handleExecutePrediction(initialVariant);
    }
  }, [initialVariant]);

  const presetExamples: { name: string; tag: string; variant: VariantInput }[] = [
    {
      name: 'TP53 Hotspot (p.Arg282Trp)',
      tag: 'Pathogenic Missense',
      variant: {
        chromosome: '17',
        position: 7673802,
        reference_allele: 'C',
        alternate_allele: 'T',
        gene_symbol: 'TP53',
        variant_type: 'single nucleotide variant',
        hgvs_name: 'NM_000546.5(TP53):c.844C>T (p.Arg282Trp)'
      }
    },
    {
      name: 'CFTR Synonymous (p.Glu528=)',
      tag: 'Benign Silent',
      variant: {
        chromosome: '7',
        position: 117175400,
        reference_allele: 'A',
        alternate_allele: 'G',
        gene_symbol: 'CFTR',
        variant_type: 'single nucleotide variant',
        hgvs_name: 'NM_000492.3(CFTR):c.1584G>A (p.Glu528=)'
      }
    },
    {
      name: 'BRCA1 Stop Gain (p.Gln232Ter)',
      tag: 'Pathogenic LoF',
      variant: {
        chromosome: '17',
        position: 43094692,
        reference_allele: 'C',
        alternate_allele: 'T',
        gene_symbol: 'BRCA1',
        variant_type: 'single nucleotide variant',
        hgvs_name: 'NM_007294.4(BRCA1):c.694C>T (p.Gln232Ter)'
      }
    },
    {
      name: 'LDLR Familial Hypercholesterolemia',
      tag: 'Pathogenic Missense',
      variant: {
        chromosome: '19',
        position: 11100236,
        reference_allele: 'G',
        alternate_allele: 'A',
        gene_symbol: 'LDLR',
        variant_type: 'single nucleotide variant',
        hgvs_name: 'NM_000527.5(LDLR):c.662G>A (p.Cys221Tyr)'
      }
    }
  ];

  const handleInputChange = (field: keyof VariantInput, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleExecutePrediction = async (customPayload?: VariantInput) => {
    const payload = customPayload || formData;
    setLoading(true);
    setError(null);
    try {
      const res = await predictVariant(payload);
      setPrediction(res);
    } catch (err: any) {
      setError(err.message || 'An error occurred during variant inference.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData({
      chromosome: '1',
      position: 1000000,
      reference_allele: 'A',
      alternate_allele: 'G',
      gene_symbol: '',
      variant_type: 'single nucleotide variant',
      hgvs_name: '',
    });
    setPrediction(null);
    setError(null);
  };

  const chromosomes = [
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
    '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
    '21', '22', 'X', 'Y', 'MT'
  ];

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      {/* Page Title Header */}
      <div>
        <div className="flex items-center space-x-2 text-xs text-slate-500 mb-1">
          <span>Inference Console</span>
          <ChevronRight className="w-3.5 h-3.5" />
          <span className="text-slate-800 font-medium">Variant Classification</span>
        </div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Variant Impact Analysis</h2>
        <p className="text-xs text-slate-500 mt-1">
          Submit genetic coordinates and allelic changes in GRCh38 assembly to compute clinical consequence probability.
        </p>
      </div>

      {/* Preset Pickers */}
      <div className="bg-slate-50/70 border border-slate-200 rounded-lg p-3.5 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-700">
          <BookOpen className="w-4 h-4 text-scientific-700" />
          <span>Load Benchmarked Clinical Case:</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {presetExamples.map((ex, i) => (
            <button
              key={i}
              onClick={() => {
                setFormData(ex.variant);
                handleExecutePrediction(ex.variant);
              }}
              className="text-xs bg-white hover:bg-slate-100 border border-slate-200 text-slate-800 font-medium px-2.5 py-1.5 rounded transition-colors shadow-2xs flex items-center space-x-1.5"
            >
              <span>{ex.name}</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${
                ex.tag.includes('Benign') ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
              }`}>
                {ex.tag}
              </span>
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Form Column (5 Cols) */}
        <div className="lg:col-span-5 bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-5">
          <div className="border-b border-slate-100 pb-3">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Genetic Variant Input</h3>
            <p className="text-xs text-slate-500 mt-0.5">Reference Assembly: GRCh38 / hg38</p>
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleExecutePrediction();
            }}
            className="space-y-4"
          >
            {/* Chromosome & Position */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Chromosome <span className="text-rose-500">*</span>
                </label>
                <select
                  value={formData.chromosome}
                  onChange={(e) => handleInputChange('chromosome', e.target.value)}
                  className="w-full text-xs font-mono bg-white border border-slate-300 rounded-md px-3 py-2 text-slate-900 focus:border-scientific-600"
                >
                  {chromosomes.map(c => (
                    <option key={c} value={c}>chr{c}</option>
                  ))}
                </select>
                <span className="text-[10px] text-slate-400 mt-0.5 block">Autosomes 1-22, X, Y, MT</span>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Genomic Position <span className="text-rose-500">*</span>
                </label>
                <input
                  type="number"
                  required
                  min={1}
                  value={formData.position}
                  onChange={(e) => handleInputChange('position', parseInt(e.target.value) || 1)}
                  className="w-full text-xs font-mono bg-white border border-slate-300 rounded-md px-3 py-2 text-slate-900 focus:border-scientific-600"
                  placeholder="e.g. 7673802"
                />
                <span className="text-[10px] text-slate-400 mt-0.5 block">1-based GRCh38 base position</span>
              </div>
            </div>

            {/* Reference & Alternate Alleles */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Reference Allele <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.reference_allele}
                  onChange={(e) => handleInputChange('reference_allele', e.target.value.toUpperCase())}
                  className="w-full text-xs font-mono bg-white border border-slate-300 rounded-md px-3 py-2 text-slate-900 focus:border-scientific-600 font-bold"
                  placeholder="e.g. C"
                />
                <span className="text-[10px] text-slate-400 mt-0.5 block">Wild-type base (A, C, G, T)</span>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Alternate Allele <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.alternate_allele}
                  onChange={(e) => handleInputChange('alternate_allele', e.target.value.toUpperCase())}
                  className="w-full text-xs font-mono bg-white border border-slate-300 rounded-md px-3 py-2 text-slate-900 focus:border-scientific-600 font-bold"
                  placeholder="e.g. T"
                />
                <span className="text-[10px] text-slate-400 mt-0.5 block">Mutant base or insertion/deletion</span>
              </div>
            </div>

            {/* Gene Symbol */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                HGNC Gene Symbol <span className="text-slate-400 font-normal">(Optional)</span>
              </label>
              <input
                type="text"
                value={formData.gene_symbol}
                onChange={(e) => handleInputChange('gene_symbol', e.target.value.toUpperCase())}
                className="w-full text-xs font-mono bg-white border border-slate-300 rounded-md px-3 py-2 text-slate-900 focus:border-scientific-600"
                placeholder="e.g. TP53, BRCA1, CFTR, LDLR"
              />
              <span className="text-[10px] text-slate-400 mt-0.5 block">Enables empirical Bayes gene constraint prior lookup</span>
            </div>

            {/* Variant Type */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Variant Classification Type
              </label>
              <select
                value={formData.variant_type}
                onChange={(e) => handleInputChange('variant_type', e.target.value)}
                className="w-full text-xs bg-white border border-slate-300 rounded-md px-3 py-2 text-slate-900 focus:border-scientific-600"
              >
                <option value="single nucleotide variant">Single Nucleotide Variant (SNV / SNP)</option>
                <option value="deletion">Deletion</option>
                <option value="insertion">Insertion</option>
                <option value="indel">Indel</option>
              </select>
            </div>

            {/* HGVS Nomenclature (Optional) */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                HGVS Nomenclature <span className="text-slate-400 font-normal">(Optional)</span>
              </label>
              <input
                type="text"
                value={formData.hgvs_name || ''}
                onChange={(e) => handleInputChange('hgvs_name', e.target.value)}
                className="w-full text-xs font-mono bg-white border border-slate-300 rounded-md px-3 py-2 text-slate-900 focus:border-scientific-600"
                placeholder="e.g. NM_000546.5:c.844C>T (p.Arg282Trp)"
              />
              <span className="text-[10px] text-slate-400 mt-0.5 block">Extracts codon change, amino acid swap &amp; Grantham score</span>
            </div>

            {/* Actions */}
            <div className="pt-2 flex items-center space-x-3">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 inline-flex items-center justify-center space-x-2 bg-scientific-800 hover:bg-scientific-700 text-white font-medium py-2.5 px-4 rounded-lg text-xs transition-colors shadow-sm disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    <span>Processing Inference...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-3.5 h-3.5 fill-current" />
                    <span>Run Clinical Prediction</span>
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={handleReset}
                disabled={loading}
                className="inline-flex items-center justify-center text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 py-2.5 px-3 rounded-lg text-xs transition-colors"
                title="Reset form"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            </div>
          </form>
        </div>

        {/* Right Prediction Output Column (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {error && (
            <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 flex items-start space-x-3 text-rose-900 text-xs">
              <AlertTriangle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
              <div>
                <strong className="font-semibold block mb-0.5">Inference Request Failed</strong>
                <span>{error}</span>
              </div>
            </div>
          )}

          {prediction ? (
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-6">
              {/* Prediction Summary Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-3">
                <div>
                  <span className="text-[10px] font-semibold tracking-wider uppercase text-slate-400 block mb-1">
                    Model Classification Result
                  </span>
                  <div className="flex items-center space-x-3">
                    <span
                      className={`inline-flex items-center text-base font-bold px-3 py-1 rounded-md border ${
                        prediction.classification === 'Pathogenic'
                          ? 'bg-rose-50 text-rose-800 border-rose-200'
                          : 'bg-emerald-50 text-emerald-800 border-emerald-200'
                      }`}
                    >
                      {prediction.classification === 'Pathogenic' ? (
                        <AlertTriangle className="w-4 h-4 mr-1.5 text-rose-600" />
                      ) : (
                        <CheckCircle2 className="w-4 h-4 mr-1.5 text-emerald-600" />
                      )}
                      {prediction.classification}
                    </span>
                    <span className="text-xs text-slate-500">
                      Risk Tier: <strong className="text-slate-800 font-semibold">{prediction.risk_level}</strong>
                    </span>
                  </div>
                </div>

                <div className="text-right sm:border-l sm:border-slate-100 sm:pl-4">
                  <span className="text-[10px] text-slate-400 block">Calculated Confidence</span>
                  <span className="text-lg font-bold font-mono text-slate-900">
                    {(prediction.confidence_score * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              {/* Probability Spectrum Gauge */}
              <div className="space-y-2">
                <div className="flex justify-between text-xs text-slate-600">
                  <span>Estimated Class Probability Distribution:</span>
                  <span className="font-mono text-slate-800 font-medium">
                    Benign {(prediction.probability_benign * 100).toFixed(1)}% | Pathogenic {(prediction.probability_pathogenic * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden flex border border-slate-200">
                  <div
                    style={{ width: `${prediction.probability_benign * 100}%` }}
                    className="bg-emerald-500 transition-all duration-500"
                    title={`Benign: ${(prediction.probability_benign * 100).toFixed(1)}%`}
                  ></div>
                  <div
                    style={{ width: `${prediction.probability_pathogenic * 100}%` }}
                    className="bg-rose-500 transition-all duration-500"
                    title={`Pathogenic: ${(prediction.probability_pathogenic * 100).toFixed(1)}%`}
                  ></div>
                </div>
                <p className="text-[11px] text-slate-400 italic">
                  Note: Probability estimates are generated by Random Forest leaf voting across 150 decision estimators and represent model confidence against ClinVar distributions.
                </p>
              </div>

              {/* Submitted Variant Specification Grid */}
              <div className="bg-slate-50/80 rounded-lg p-3.5 border border-slate-200">
                <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-2">Variant Coordinates (GRCh38)</h4>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
                  <div>
                    <span className="text-slate-400 block text-[10px]">Locus</span>
                    <span className="text-slate-900 font-medium">chr{prediction.submitted_variant.chromosome}:{prediction.submitted_variant.position.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Allele Swap</span>
                    <span className="text-slate-900 font-medium">{prediction.submitted_variant.reference_allele} &gt; {prediction.submitted_variant.alternate_allele}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Gene Symbol</span>
                    <span className="text-slate-900 font-medium">{prediction.submitted_variant.gene_symbol || 'UNKNOWN'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Type</span>
                    <span className="text-slate-900 font-medium">{prediction.submitted_variant.variant_type}</span>
                  </div>
                </div>
              </div>

              {/* Biological Features Breakdown */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Extracted Biological Features</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div className="bg-white border border-slate-200 rounded-md p-3">
                    <span className="text-[10px] text-slate-400 block uppercase">Consequence</span>
                    <span className="font-semibold text-slate-800">{prediction.biological_features.molecular_consequence}</span>
                  </div>
                  <div className="bg-white border border-slate-200 rounded-md p-3">
                    <span className="text-[10px] text-slate-400 block uppercase">Mutational Mechanism</span>
                    <span className="font-semibold text-slate-800">{prediction.biological_features.mutation_mechanism}</span>
                  </div>
                  <div className="bg-white border border-slate-200 rounded-md p-3">
                    <span className="text-[10px] text-slate-400 block uppercase">Grantham Physicochemical Distance</span>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono font-bold text-slate-900">{prediction.biological_features.grantham_distance.toFixed(0)}</span>
                      <span className="text-slate-500 text-[11px]">
                        {prediction.biological_features.grantham_distance > 100
                          ? '(Radical change)'
                          : prediction.biological_features.grantham_distance === 0
                          ? '(Conservative / Silent)'
                          : '(Moderate)'}
                      </span>
                    </div>
                  </div>
                  <div className="bg-white border border-slate-200 rounded-md p-3">
                    <span className="text-[10px] text-slate-400 block uppercase">Gene Constraint Propensity</span>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono font-bold text-slate-900">{prediction.biological_features.gene_pathogenicity_propensity.toFixed(3)}</span>
                      <span className="text-slate-500 text-[11px]">(Empirical Bayes prior)</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Scientific Explanation */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Interpretation Rationale</h4>
                <div className="bg-scientific-50/50 border border-scientific-200/70 rounded-lg p-3.5 text-xs text-slate-700 leading-relaxed">
                  {prediction.explanation}
                </div>
              </div>

              {/* External Annotation Card */}
              {prediction.external_annotation && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-slate-900 uppercase tracking-wider">External Gene Annotation</span>
                    <span className="text-[11px] text-slate-500 font-mono">Source: {prediction.external_annotation.source}</span>
                  </div>
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs space-y-1">
                    <div className="flex items-center space-x-2">
                      <strong className="text-slate-900">{prediction.external_annotation.gene_symbol}</strong>
                      {prediction.external_annotation.ensembl_id && (
                        <span className="text-slate-500 font-mono text-[11px]">({prediction.external_annotation.ensembl_id})</span>
                      )}
                      {prediction.external_annotation.chromosome_location && (
                        <span className="text-slate-500 text-[11px]">• Location: {prediction.external_annotation.chromosome_location}</span>
                      )}
                    </div>
                    <p className="text-slate-600 leading-relaxed text-[11px]">
                      {prediction.external_annotation.gene_description}
                    </p>
                  </div>
                </div>
              )}

              {/* Scientific Disclaimer */}
              <div className="border-t border-slate-100 pt-4 flex items-start space-x-2 text-[11px] text-slate-500 italic">
                <ShieldAlert className="w-3.5 h-3.5 text-amber-600 flex-shrink-0 mt-0.5" />
                <span>{prediction.scientific_disclaimer}</span>
              </div>
            </div>
          ) : (
            <div className="bg-white border border-slate-200 border-dashed rounded-xl p-12 text-center text-slate-400 space-y-3">
              <Dna className="w-10 h-10 mx-auto text-slate-300 stroke-1" />
              <div>
                <h3 className="text-sm font-semibold text-slate-700">No Variant Analyzed Yet</h3>
                <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
                  Configure the genetic coordinates on the left or select a benchmarked case from the presets above to view model predictions and molecular features.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
