import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { DashboardPage } from './pages/DashboardPage';
import { PredictPage } from './pages/PredictPage';
import { ModelPerformancePage } from './pages/ModelPerformancePage';
import { DatasetPage } from './pages/DatasetPage';
import { AboutPage } from './pages/AboutPage';

import { getModelInfo, getDatasetSummary, checkHealth } from './services/api';
import { ModelInfoResponse, DatasetSummaryResponse, HealthResponse, VariantInput } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [modelInfo, setModelInfo] = useState<ModelInfoResponse | null>(null);
  const [datasetSummary, setDatasetSummary] = useState<DatasetSummaryResponse | null>(null);
  const [presetVariant, setPresetVariant] = useState<VariantInput | undefined>(undefined);

  useEffect(() => {
    // Initial fetch of system health, model info, and dataset summary
    checkHealth()
      .then(res => setHealth(res))
      .catch(() => setHealth({ status: 'degraded', service_name: 'Mutation Impact AI', version: '1.0.0', model_loaded: false }));

    getModelInfo()
      .then(info => setModelInfo(info))
      .catch(err => console.warn('Could not load model info:', err));

    getDatasetSummary()
      .then(summary => setDatasetSummary(summary))
      .catch(err => console.warn('Could not load dataset summary:', err));
  }, []);

  const handleNavigateToPredict = (variant?: VariantInput) => {
    if (variant) {
      setPresetVariant(variant);
    }
    setActiveTab('predict');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleNavigateToPerformance = () => {
    setActiveTab('performance');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen flex flex-col bg-ivory-100 text-slate-800">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        health={health}
      />

      <main className="flex-1">
        {activeTab === 'dashboard' && (
          <DashboardPage
            onNavigateToPredict={handleNavigateToPredict}
            onNavigateToPerformance={handleNavigateToPerformance}
            modelInfo={modelInfo}
            datasetSummary={datasetSummary}
          />
        )}

        {activeTab === 'predict' && (
          <PredictPage initialVariant={presetVariant} />
        )}

        {activeTab === 'performance' && (
          <ModelPerformancePage modelInfo={modelInfo} />
        )}

        {activeTab === 'dataset' && (
          <DatasetPage datasetSummary={datasetSummary} />
        )}

        {activeTab === 'about' && (
          <AboutPage />
        )}
      </main>

      <Footer />
    </div>
  );
};

export default App;
