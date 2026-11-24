import React from 'react';
import { BookOpen, ShieldAlert, Cpu, Dna, Code } from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-10">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-xs text-slate-500 mb-1">
          <span>Documentation</span>
          <span>•</span>
          <span className="text-slate-800 font-medium">Research Background &amp; Architecture</span>
        </div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">About Mutation Impact AI</h2>
        <p className="text-xs text-slate-500 mt-1 max-w-2xl">
          An autonomous, full-stack computational genomics platform engineered for predicting the deleterious functional impact of human genetic variants and SNPs.
        </p>
      </div>

      {/* Problem Statement & Mission */}
      <section className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
          <Dna className="w-4 h-4 text-scientific-700" />
          <span>The Clinical Genomics Challenge</span>
        </h3>
        <p className="text-xs text-slate-700 leading-relaxed">
          High-throughput next-generation sequencing (NGS) routinely identifies millions of genomic variants in individual patients. However, the vast majority of identified variants are novel or lack functional characterization, creating a massive clinical bottleneck known as <strong>Variants of Uncertain Significance (VUS)</strong>. Distinguishing truly disease-causing (pathogenic) mutations from neutral, benign polymorphisms is essential for rare disease diagnosis, cancer predisposition screening, and precision medicine.
        </p>
        <p className="text-xs text-slate-700 leading-relaxed">
          <strong>Mutation Impact AI</strong> solves this challenge by implementing an end-to-end machine learning system trained on authentic, peer-reviewed clinical interpretations from NCBI ClinVar. Rather than relying on superficial sequence matching, the system extracts 29 biologically motivated features encompassing physicochemical amino acid divergence (Grantham score), codon disruption mechanics, Loss-of-Function consequences, and gene-level selective constraint.
        </p>
      </section>

      {/* Methodology & Biological Features */}
      <section className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-6">
        <div>
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-scientific-700" />
            <span>Biologically Motivated Feature Engineering</span>
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Features are derived directly from the variant&apos;s genomic coordinates, nucleotide swap, and HGVS nomenclature without target data leakage:
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="border border-slate-200 rounded-lg p-4 space-y-2 bg-slate-50/50">
            <h4 className="font-bold text-slate-900">1. Grantham Physicochemical Distance Matrix</h4>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              Quantifies the chemical divergence between reference and mutant amino acid residues based on atomic composition, polarity, and molecular volume (Grantham R., Science 1974). Radical substitutions (distance &gt; 100, such as Cys to Trp or Arg to Leu) destabilize protein tertiary folding.
            </p>
          </div>

          <div className="border border-slate-200 rounded-lg p-4 space-y-2 bg-slate-50/50">
            <h4 className="font-bold text-slate-900">2. Loss-of-Function (LoF) Consequence Extraction</h4>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              Systematically detects premature termination codons (nonsense / stop-gain), reading frame alterations (frameshifting indels), and canonical splice donor/acceptor site disruptions (+/- 1-2 bp from exon-intron junctions) aligning with ACMG/AMP PVS1 strong pathogenic criteria.
            </p>
          </div>

          <div className="border border-slate-200 rounded-lg p-4 space-y-2 bg-slate-50/50">
            <h4 className="font-bold text-slate-900">3. Mutational Chemistry &amp; CpG Deamination</h4>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              Differentiates purine-to-purine and pyrimidine-to-pyrimidine transitions from transversions, specifically identifying CpG island methylation-mediated spontaneous deamination hotspots (C&gt;T and G&gt;A).
            </p>
          </div>

          <div className="border border-slate-200 rounded-lg p-4 space-y-2 bg-slate-50/50">
            <h4 className="font-bold text-slate-900">4. Empirical Bayes Gene Pathogenicity Prior</h4>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              Computes a smoothed posterior pathogenicity propensity score per gene, accounting for biological intolerance to variation in critical tumor suppressors (TP53, BRCA1, LDLR) versus neutral structural proteins, fitted strictly on training data folds.
            </p>
          </div>
        </div>
      </section>

      {/* Technology Stack Grid */}
      <section className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
          <Code className="w-4 h-4 text-scientific-700" />
          <span>Technology Stack</span>
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
            <span className="text-[10px] text-slate-400 block uppercase font-mono">Machine Learning</span>
            <span className="font-bold text-slate-900">Scikit-learn</span>
            <p className="text-[11px] text-slate-500 mt-0.5">Random Forest, NumPy, Pandas, Joblib</p>
          </div>
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
            <span className="text-[10px] text-slate-400 block uppercase font-mono">Backend API</span>
            <span className="font-bold text-slate-900">FastAPI</span>
            <p className="text-[11px] text-slate-500 mt-0.5">Pydantic v2, Uvicorn, Python 3.14</p>
          </div>
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
            <span className="text-[10px] text-slate-400 block uppercase font-mono">Frontend Interface</span>
            <span className="font-bold text-slate-900">React &amp; TypeScript</span>
            <p className="text-[11px] text-slate-500 mt-0.5">Vite, Lucide-React</p>
          </div>
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
            <span className="text-[10px] text-slate-400 block uppercase font-mono">Design System</span>
            <span className="font-bold text-slate-900">Tailwind CSS</span>
            <p className="text-[11px] text-slate-500 mt-0.5">Biotechnology palette, Inter &amp; JetBrains Mono</p>
          </div>
        </div>
      </section>

      {/* Ethical Boundaries & Scientific Disclaimer */}
      <section className="bg-amber-50/70 border border-amber-200 rounded-xl p-6 space-y-3 text-amber-900">
        <div className="flex items-center space-x-2 font-bold text-sm">
          <ShieldAlert className="w-5 h-5 text-amber-700" />
          <span>Ethical Boundaries &amp; Regulatory Guidance</span>
        </div>
        <p className="text-xs leading-relaxed">
          <strong>This application provides research-oriented machine learning predictions based on its training data. Predictions are not medical diagnoses and should not be used for clinical decision-making.</strong>
        </p>
        <p className="text-xs leading-relaxed text-amber-800">
          In clinical diagnostic environments (e.g. CLIA/CAP accredited laboratories), genetic variant interpretations must conform to ACMG/AMP consensus guidelines, combining clinical family history, population allele frequencies (gnomAD), segregation studies, functional cell assays, and multi-disciplinary molecular tumor board review.
        </p>
      </section>

      {/* Key Academic Citations */}
      <section className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-3 text-xs">
        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
          <BookOpen className="w-4 h-4 text-scientific-700" />
          <span>Key Scientific Citations</span>
        </h3>
        <ul className="space-y-2 text-slate-600">
          <li>
            1. <strong>Landrum MJ, et al.</strong> (2020). ClinVar: improving access to variant interpretations and supporting evidence. <em>Nucleic Acids Research</em>, 48(D1):D835-D844.
          </li>
          <li>
            2. <strong>Richards S, et al.</strong> (2015). Standards and guidelines for the interpretation of sequence variants: a joint consensus recommendation of the ACMG and AMP. <em>Genetics in Medicine</em>, 17(5):405-424.
          </li>
          <li>
            3. <strong>Grantham R.</strong> (1974). Amino acid difference formula to help explain protein evolution. <em>Science</em>, 185(4154):862-864.
          </li>
        </ul>
      </section>
    </div>
  );
};
