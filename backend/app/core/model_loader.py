"""
Model Loader Singleton
Mutation Impact AI - Backend
"""

import os
import sys
import json
import joblib
from typing import Optional, Dict, Any

from backend.app.core.config import settings, PROJECT_ROOT

# Ensure project root is in sys.path so unpickling ml.preprocess works cleanly
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

class ModelManager:
    _instance: Optional["ModelManager"] = None
    
    def __init__(self):
        self.pipeline = None
        self.metrics: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.dataset_summary: Dict[str, Any] = {}
        self.is_loaded: bool = False

    @classmethod
    def get_instance(cls) -> "ModelManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_artifacts(self):
        """Loads machine learning model pipeline and associated metadata once at startup."""
        print(f"[*] Loading model pipeline from: {settings.MODEL_PATH}")
        if not os.path.exists(settings.MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at: {settings.MODEL_PATH}")
            
        self.pipeline = joblib.load(settings.MODEL_PATH)
        
        if os.path.exists(settings.METRICS_PATH):
            with open(settings.METRICS_PATH, "r", encoding="utf-8") as f:
                self.metrics = json.load(f)
                
        if os.path.exists(settings.METADATA_PATH):
            with open(settings.METADATA_PATH, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
                
        if os.path.exists(settings.DATASET_SUMMARY_PATH):
            with open(settings.DATASET_SUMMARY_PATH, "r", encoding="utf-8") as f:
                self.dataset_summary = json.load(f)
                
        self.is_loaded = True
        print("[+] Model artifacts successfully loaded into memory!")

model_manager = ModelManager.get_instance()
