import React from 'react';
import { Dna, Activity, BarChart3, Database, Info, CheckCircle2, AlertCircle } from 'lucide-react';
import { HealthResponse } from '../types';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  health: HealthResponse | null;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, health }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'predict', label: 'Variant Prediction', icon: Dna },
    { id: 'performance', label: 'Model Performance', icon: BarChart3 },
    { id: 'dataset', label: 'Dataset Info', icon: Database },
    { id: 'about', label: 'About & Methodology', icon: Info },
  ];

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
      {/* Top utility bar */}
      <div className="bg-scientific-950 text-slate-300 text-xs px-6 py-1.5 flex justify-between items-center border-b border-scientific-900">
        <div className="flex items-center space-x-2">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="font-medium tracking-wide">NCBI ClinVar GRCh38 Reference Pipeline</span>
          <span className="text-slate-500">•</span>
          <span className="text-slate-400">Research & Diagnostic Portfolio Platform</span>
        </div>
        <div className="flex items-center space-x-4">
          <span className="text-slate-400">Model: <strong className="text-emerald-300 font-mono font-normal">Random Forest v1.0.0</strong></span>
          <div className="flex items-center space-x-1.5">
            {health?.status === 'healthy' ? (
              <span className="inline-flex items-center text-emerald-400 font-mono">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> API Online
              </span>
            ) : (
              <span className="inline-flex items-center text-amber-400 font-mono">
                <AlertCircle className="w-3.5 h-3.5 mr-1" /> Connecting...
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Main navigation */}
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
          <div className="w-10 h-10 rounded-lg bg-scientific-800 text-white flex items-center justify-center shadow-sm">
            <Dna className="w-6 h-6 text-emerald-300" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold text-slate-900 tracking-tight">Mutation Impact AI</h1>
              <span className="bg-scientific-50 text-scientific-800 text-[10px] font-semibold px-2 py-0.5 rounded border border-scientific-200 uppercase tracking-wider">
                Research Edition
              </span>
            </div>
            <p className="text-xs text-slate-500 font-normal">
              Functional Impact Prediction of Genetic Variants & SNPs
            </p>
          </div>
        </div>

        {/* Tab links */}
        <nav className="flex items-center space-x-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center space-x-2 px-3.5 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-scientific-50 text-scientific-900 font-semibold border-b-2 border-scientific-700'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-scientific-700' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
