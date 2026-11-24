import {
  VariantInput,
  PredictionResponse,
  ModelInfoResponse,
  DatasetSummaryResponse,
  HealthResponse,
  ExternalAnnotation
} from '../types';

const API_BASE_URL = ''; // Uses Vite proxy in development, or relative in production

export async function predictVariant(variant: VariantInput): Promise<PredictionResponse> {
  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(variant),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || `Prediction request failed with status ${response.status}`;
    throw new Error(message);
  }

  return response.json();
}

export async function getModelInfo(): Promise<ModelInfoResponse> {
  const response = await fetch(`${API_BASE_URL}/api/model/info`);
  if (!response.ok) {
    throw new Error(`Failed to load model information: ${response.statusText}`);
  }
  return response.json();
}

export async function getDatasetSummary(): Promise<DatasetSummaryResponse> {
  const response = await fetch(`${API_BASE_URL}/api/dataset/summary`);
  if (!response.ok) {
    throw new Error(`Failed to load dataset summary: ${response.statusText}`);
  }
  return response.json();
}

export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`);
  }
  return response.json();
}

export async function getGeneAnnotation(geneSymbol: string): Promise<ExternalAnnotation> {
  const response = await fetch(`${API_BASE_URL}/api/external/gene/${encodeURIComponent(geneSymbol)}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch gene annotation: ${response.statusText}`);
  }
  return response.json();
}
