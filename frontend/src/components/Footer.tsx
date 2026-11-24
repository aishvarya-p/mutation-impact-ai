import React from 'react';
import { ShieldAlert, BookOpen, ExternalLink, Dna } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-slate-200 mt-20">
      {/* Scientific disclaimer banner */}
      <div className="bg-amber-50/70 border-b border-amber-200/60 py-3.5 px-6">
        <div className="max-w-7xl mx-auto flex items-start space-x-3 text-amber-900 text-xs">
          <ShieldAlert className="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            <strong>Mandatory Scientific Disclaimer:</strong> This application provides research-oriented machine learning predictions based on its training data. Predictions are not medical diagnoses and should not be used for clinical decision-making. All variant impact evaluations require clinical geneticist review and independent experimental validation.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center space-x-2">
              <div className="w-7 h-7 rounded bg-scientific-800 text-white flex items-center justify-center">
                <Dna className="w-4 h-4 text-emerald-300" />
              </div>
              <span className="font-bold text-slate-900 text-sm">Mutation Impact AI</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed max-w-md">
              An autonomous machine learning system designed to predict whether human genetic variants (SNVs, indels, and frameshifts) exhibit benign or pathogenic clinical impact. Trained and evaluated against high-confidence ClinVar benchmark records.
            </p>
            <div className="text-xs text-slate-400 pt-1">
              Data source: NCBI ClinVar (GRCh38) • Pipeline: Scikit-learn Random Forest
            </div>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-3">Primary Resources</h4>
            <ul className="space-y-2 text-xs text-slate-600">
              <li>
                <a
                  href="https://www.ncbi.nlm.nih.gov/clinvar/"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-scientific-700 flex items-center space-x-1"
                >
                  <span>NCBI ClinVar Database</span>
                  <ExternalLink className="w-3 h-3 text-slate-400" />
                </a>
              </li>
              <li>
                <a
                  href="https://www.ensembl.org/"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-scientific-700 flex items-center space-x-1"
                >
                  <span>Ensembl Genome Browser</span>
                  <ExternalLink className="w-3 h-3 text-slate-400" />
                </a>
              </li>
              <li>
                <a
                  href="https://www.ncbi.nlm.nih.gov/snp/"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-scientific-700 flex items-center space-x-1"
                >
                  <span>dbSNP Short Genetic Variations</span>
                  <ExternalLink className="w-3 h-3 text-slate-400" />
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-3">Clinical Guidelines</h4>
            <ul className="space-y-2 text-xs text-slate-600">
              <li className="flex items-center space-x-1">
                <BookOpen className="w-3 h-3 text-slate-400" />
                <span>ACMG/AMP Variant Standards</span>
              </li>
              <li className="flex items-center space-x-1">
                <BookOpen className="w-3 h-3 text-slate-400" />
                <span>Grantham Chemical Distance (1974)</span>
              </li>
              <li className="flex items-center space-x-1">
                <BookOpen className="w-3 h-3 text-slate-400" />
                <span>Empirical Bayes Gene Scoring</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-100 mt-8 pt-6 flex flex-col md:flex-row justify-between items-center text-xs text-slate-500">
          <div>
            © {new Date().getFullYear()} Mutation Impact AI. Built for biotechnology and computational genomics research.
          </div>
          <div className="mt-2 md:mt-0 font-mono text-[11px] text-slate-400">
            FastAPI • Scikit-learn • React • Tailwind CSS
          </div>
        </div>
      </div>
    </footer>
  );
};
