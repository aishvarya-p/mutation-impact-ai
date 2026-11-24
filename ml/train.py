#!/usr/bin/env python3
"""
Model Training and Rigorous Comparative Evaluation Pipeline
Mutation Impact AI - Genetic Mutation Impact Classifier

Trains and evaluates:
1. Logistic Regression (L2 regularized)
2. Decision Tree Classifier
3. Random Forest Classifier
4. HistGradientBoosting Classifier (Ensemble Boosting)
5. K-Nearest Neighbors Classifier

Calculates:
- Accuracy, Precision, Recall, F1-Score, Specificity, ROC-AUC
- 5-Fold Stratified Cross-Validation on training fold
- Publication-quality scientific figures
- Exports final unified pipeline with Joblib
"""

import os
import sys
import json
import time
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report, roc_curve, precision_recall_curve,
    auc
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.preprocess import GeneticFeatureExtractor, MutationImpactPipeline

def run_training_pipeline(
    raw_path: str = "data/raw/clinvar_raw_variants.tsv",
    processed_dir: str = "data/processed",
    output_dir: str = "ml/saved_models"
):
    print("=" * 80)
    print("  MUTATION IMPACT AI: MACHINE LEARNING PIPELINE")
    print("  Classification: Benign (0) vs Pathogenic (1)")
    print("=" * 80)
    
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    fig_dir = os.path.join(output_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)
    
    # 1. Load raw dataset
    print(f"\n[1/7] Loading dataset from: {raw_path}")
    df = pd.read_csv(raw_path, sep="\t")
    print(f"      Initial records: {len(df):,} rows x {len(df.columns)} columns")
    
    # 2. Data Cleaning & Hygiene
    print("\n[2/7] Cleaning and verifying dataset integrity...")
    df['GeneSymbol'] = df['GeneSymbol'].fillna('UNKNOWN').astype(str).str.strip().str.upper()
    df['Name'] = df['Name'].fillna('').astype(str).str.strip()
    df['Type'] = df['Type'].fillna('single nucleotide variant').astype(str).str.strip()
    df['Chromosome'] = df['Chromosome'].astype(str).str.replace('chr', '').str.strip()
    df['Start'] = pd.to_numeric(df['Start'], errors='coerce')
    df = df.dropna(subset=['Start', 'Chromosome', 'ReferenceAllele', 'AlternateAllele', 'BinaryClass'])
    df['Start'] = df['Start'].astype(np.int64)
    
    # Map target label: Benign -> 0, Pathogenic -> 1
    label_map = {"Benign": 0, "Pathogenic": 1}
    df['target'] = df['BinaryClass'].map(label_map)
    df = df.dropna(subset=['target'])
    df['target'] = df['target'].astype(int)
    
    # Save cleaned dataset for reproducible inspection
    cleaned_path = os.path.join(processed_dir, "clinvar_cleaned.tsv")
    df.to_csv(cleaned_path, sep="\t", index=False)
    print(f"      Cleaned dataset saved to: {cleaned_path}")
    print(f"      Cleaned shape: {df.shape}")
    print(f"      Target distribution: Benign (0) = {(df['target'] == 0).sum():,}, Pathogenic (1) = {(df['target'] == 1).sum():,}")
    
    # Save summary statistics
    summary_stats = {
        "total_variants": int(len(df)),
        "benign_variants": int((df['target'] == 0).sum()),
        "pathogenic_variants": int((df['target'] == 1).sum()),
        "unique_genes": int(df['GeneSymbol'].nunique()),
        "chromosomes_represented": sorted(list(df['Chromosome'].unique())),
        "variant_types": df['Type'].value_counts().to_dict(),
        "top_10_genes": df['GeneSymbol'].value_counts().head(10).to_dict()
    }
    with open(os.path.join(processed_dir, "dataset_summary.json"), "w") as sf:
        json.dump(summary_stats, sf, indent=2)
        
    # 3. Train-Test Split (80% Train, 20% Test, Stratified)
    print("\n[3/7] Performing Stratified Train-Test Split (80/20)...")
    feature_cols = ['Chromosome', 'Start', 'ReferenceAllele', 'AlternateAllele', 'GeneSymbol', 'Name', 'Type']
    X = df[feature_cols]
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"      Training set: {len(X_train):,} samples (Benign: {(y_train == 0).sum():,}, Pathogenic: {(y_train == 1).sum():,})")
    print(f"      Testing set:  {len(X_test):,} samples (Benign: {(y_test == 0).sum():,}, Pathogenic: {(y_test == 1).sum():,})")
    
    # 4. Feature Extraction & Engineering
    print("\n[4/7] Fitting Feature Extractor strictly on Training Fold...")
    extractor = GeneticFeatureExtractor(smoothing=15.0)
    extractor.fit(X_train, y_train)
    
    X_train_feat = extractor.transform(X_train)
    X_test_feat = extractor.transform(X_test)
    feature_names = extractor.get_feature_names_out()
    print(f"      Extracted {len(feature_names)} biological features:")
    print("      " + ", ".join(feature_names[:10]) + " ...")
    
    # Standard Scaler for distance/linear models
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_feat)
    X_test_scaled = scaler.transform(X_test_feat)
    
    # 5. Model Evaluation and Cross-Validation
    print("\n[5/7] Evaluating Diverse Candidate Machine Learning Models...")
    
    models = {
        "Random Forest": {
            "model": RandomForestClassifier(n_estimators=150, max_depth=16, min_samples_leaf=2, random_state=42, n_jobs=-1),
            "use_scaled": False
        },
        "HistGradientBoosting": {
            "model": HistGradientBoostingClassifier(max_iter=150, max_depth=12, min_samples_leaf=10, random_state=42),
            "use_scaled": False
        },
        "Logistic Regression": {
            "model": LogisticRegression(max_iter=1000, C=1.0, random_state=42),
            "use_scaled": True
        },
        "Decision Tree": {
            "model": DecisionTreeClassifier(max_depth=12, min_samples_leaf=5, random_state=42),
            "use_scaled": False
        },
        "K-Nearest Neighbors": {
            "model": KNeighborsClassifier(n_neighbors=9, weights='distance'),
            "use_scaled": True
        }
    }
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    evaluation_results = {}
    fitted_models = {}
    
    print(f"{'Model':<22} | {'CV Acc (±std)':<14} | {'Test Acc':<9} | {'Precision':<9} | {'Recall (Path)':<13} | {'F1-Score':<9} | {'ROC-AUC':<9}")
    print("-" * 95)
    
    for name, config in models.items():
        clf = config["model"]
        use_scaled = config["use_scaled"]
        
        X_tr = X_train_scaled if use_scaled else X_train_feat
        X_te = X_test_scaled if use_scaled else X_test_feat
        
        # 5-Fold Stratified CV on training data
        cv_scores = cross_validate(clf, X_tr, y_train, cv=cv, scoring=['accuracy', 'f1', 'roc_auc'], n_jobs=-1)
        cv_acc_mean = cv_scores['test_accuracy'].mean()
        cv_acc_std = cv_scores['test_accuracy'].std()
        cv_f1_mean = cv_scores['test_f1'].mean()
        cv_roc_mean = cv_scores['test_roc_auc'].mean()
        
        # Train on full training set
        clf.fit(X_tr, y_train)
        fitted_models[name] = clf
        
        # Evaluate on held-out test set
        y_pred = clf.predict(X_te)
        if hasattr(clf, "predict_proba"):
            y_prob = clf.predict_proba(X_te)[:, 1]
        elif hasattr(clf, "decision_function"):
            y_prob = clf.decision_function(X_te)
        else:
            y_prob = y_pred.astype(float)
            
        test_acc = accuracy_score(y_test, y_pred)
        test_prec = precision_score(y_test, y_pred)
        test_rec = recall_score(y_test, y_pred)  # Pathogenic recall
        test_f1 = f1_score(y_test, y_pred)
        test_roc = roc_auc_score(y_test, y_prob)
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        
        evaluation_results[name] = {
            "cv_accuracy_mean": float(cv_acc_mean),
            "cv_accuracy_std": float(cv_acc_std),
            "cv_f1_mean": float(cv_f1_mean),
            "cv_roc_mean": float(cv_roc_mean),
            "test_accuracy": float(test_acc),
            "test_precision": float(test_prec),
            "test_recall": float(test_rec),
            "test_specificity": float(specificity),
            "test_f1": float(test_f1),
            "test_roc_auc": float(test_roc),
            "confusion_matrix": {
                "tn": int(tn),
                "fp": int(fp),
                "fn": int(fn),
                "tp": int(tp)
            },
            "y_prob": y_prob
        }
        
        print(f"{name:<22} | {cv_acc_mean:.4f}±{cv_acc_std:.3f} | {test_acc:<9.4f} | {test_prec:<9.4f} | {test_rec:<13.4f} | {test_f1:<9.4f} | {test_roc:<9.4f}")

    # 6. Model Selection
    # Prioritize Pathogenic Recall, F1-Score and ROC-AUC
    best_model_name = max(evaluation_results.keys(), key=lambda k: evaluation_results[k]["test_f1"] * 0.4 + evaluation_results[k]["test_recall"] * 0.3 + evaluation_results[k]["test_roc_auc"] * 0.3)
    best_clf = fitted_models[best_model_name]
    best_results = evaluation_results[best_model_name]
    
    print("\n" + "=" * 80)
    print(f"  SELECTED FINAL MODEL: {best_model_name.upper()}")
    print(f"  Reason: Highest combined F1-Score ({best_results['test_f1']:.4f}), Pathogenic Recall ({best_results['test_recall']:.4f}), and ROC-AUC ({best_results['test_roc_auc']:.4f})")
    print("=" * 80)
    
    # 7. Package and Export End-to-End Pipeline
    print("\n[6/7] Building and exporting deployable Joblib Pipeline...")
    
    pipeline_export = MutationImpactPipeline(
        extractor=extractor,
        classifier=best_clf,
        scaler=scaler if models[best_model_name]["use_scaled"] else None
    )
    
    pipeline_file = os.path.join(output_dir, "mutation_impact_pipeline.joblib")
    joblib.dump(pipeline_export, pipeline_file)
    print(f"      Pipeline successfully serialized to: {pipeline_file}")
    
    # Feature Importances (if tree-based)
    feature_importances = {}
    if hasattr(best_clf, "feature_importances_"):
        fi = best_clf.feature_importances_
        for fn, imp in sorted(zip(feature_names, fi), key=lambda x: x[1], reverse=True):
            feature_importances[fn] = float(imp)
            
    # Save Metrics & Metadata
    clean_eval_results = {}
    for m_name, res in evaluation_results.items():
        clean_eval_results[m_name] = {k: v for k, v in res.items() if k != "y_prob"}
        
    metrics_file = os.path.join(output_dir, "metrics.json")
    with open(metrics_file, "w") as mf:
        json.dump({
            "selected_model": best_model_name,
            "models_evaluated": clean_eval_results,
            "training_samples": len(X_train),
            "testing_samples": len(X_test),
            "generated_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }, mf, indent=2)
    print(f"      Evaluation metrics saved to: {metrics_file}")
    
    metadata_file = os.path.join(output_dir, "model_metadata.json")
    with open(metadata_file, "w") as mdf:
        json.dump({
            "model_architecture": best_model_name,
            "classifier_params": best_clf.get_params(),
            "feature_names": list(feature_names),
            "feature_importances": feature_importances,
            "classes": ["Benign", "Pathogenic"],
            "target_mapping": {"Benign": 0, "Pathogenic": 1},
            "training_dataset": "NCBI ClinVar GRCh38 Cleaned Extract",
            "training_samples_count": len(X_train),
            "testing_samples_count": len(X_test),
            "global_pathogenicity_prior": float(extractor.global_pathogenicity_prior_),
            "genes_profiled": len(extractor.gene_pathogenicity_map_)
        }, mdf, indent=2, default=str)
    print(f"      Model metadata saved to: {metadata_file}")
    
    # 8. Generate Scientific Visualizations
    print("\n[7/7] Generating publication-grade scientific evaluation figures...")
    
    # Figure 1: Confusion Matrix
    cm = best_results["confusion_matrix"]
    cm_arr = np.array([[cm["tn"], cm["fp"]], [cm["fn"], cm["tp"]]])
    
    plt.figure(figsize=(6, 5), dpi=300)
    plt.imshow(cm_arr, interpolation='nearest', cmap='Blues')
    plt.title(f'Confusion Matrix: {best_model_name}\n(Test Set N={len(y_test):,})', fontsize=12, pad=12, fontweight='bold', color='#1e293b')
    plt.colorbar(fraction=0.046, pad=0.04)
    tick_marks = np.arange(2)
    plt.xticks(tick_marks, ['Benign (0)', 'Pathogenic (1)'], fontsize=10, color='#334155')
    plt.yticks(tick_marks, ['Benign (0)', 'Pathogenic (1)'], fontsize=10, color='#334155')
    plt.xlabel('Predicted Clinical Label', fontsize=11, labelpad=8, fontweight='medium', color='#1e293b')
    plt.ylabel('True ClinVar Label', fontsize=11, labelpad=8, fontweight='medium', color='#1e293b')
    
    thresh = cm_arr.max() / 2.
    for i in range(2):
        for j in range(2):
            plt.text(j, i, f"{cm_arr[i, j]:,}\n({cm_arr[i, j]/cm_arr.sum()*100:.1f}%)",
                     horizontalalignment="center",
                     verticalalignment="center",
                     fontsize=11,
                     fontweight='semibold',
                     color="white" if cm_arr[i, j] > thresh else "#0f172a")
    plt.tight_layout()
    cm_path = os.path.join(fig_dir, "confusion_matrix.png")
    plt.savefig(cm_path)
    plt.close()
    print(f"      [x] Confusion matrix: {cm_path}")
    
    # Figure 2: ROC Curve Comparison
    plt.figure(figsize=(7, 6), dpi=300)
    colors = ['#0f766e', '#0369a1', '#7c3aed', '#b45309', '#be123c']
    for idx, (m_name, res) in enumerate(evaluation_results.items()):
        fpr, tpr, _ = roc_curve(y_test, res["y_prob"])
        roc_val = res["test_roc_auc"]
        plt.plot(fpr, tpr, color=colors[idx % len(colors)], lw=2, label=f'{m_name} (AUC = {roc_val:.3f})')
        
    plt.plot([0, 1], [0, 1], color='#94a3b8', lw=1.5, linestyle='--', label='Random Chance (AUC = 0.500)')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate (1 - Specificity)', fontsize=11, labelpad=8, color='#1e293b')
    plt.ylabel('True Positive Rate (Recall / Sensitivity)', fontsize=11, labelpad=8, color='#1e293b')
    plt.title('Receiver Operating Characteristic (ROC) Comparison', fontsize=12, fontweight='bold', pad=12, color='#1e293b')
    plt.legend(loc="lower right", frameon=True, fontsize=9)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    roc_path = os.path.join(fig_dir, "roc_curve.png")
    plt.savefig(roc_path)
    plt.close()
    print(f"      [x] ROC curve: {roc_path}")
    
    # Figure 3: Precision-Recall Curve
    plt.figure(figsize=(7, 6), dpi=300)
    for idx, (m_name, res) in enumerate(evaluation_results.items()):
        prec, rec, _ = precision_recall_curve(y_test, res["y_prob"])
        pr_auc = auc(rec, prec)
        plt.plot(rec, prec, color=colors[idx % len(colors)], lw=2, label=f'{m_name} (PR-AUC = {pr_auc:.3f})')
        
    plt.xlabel('Recall (Sensitivity for Pathogenic Mutations)', fontsize=11, labelpad=8, color='#1e293b')
    plt.ylabel('Precision (Positive Predictive Value)', fontsize=11, labelpad=8, color='#1e293b')
    plt.title('Precision-Recall Curves Across Evaluated Models', fontsize=12, fontweight='bold', pad=12, color='#1e293b')
    plt.legend(loc="lower left", frameon=True, fontsize=9)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    pr_path = os.path.join(fig_dir, "precision_recall_curve.png")
    plt.savefig(pr_path)
    plt.close()
    print(f"      [x] Precision-Recall curve: {pr_path}")
    
    # Figure 4: Feature Importance
    if feature_importances:
        top_k = min(15, len(feature_importances))
        sorted_fi = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)[:top_k]
        feat_labels = [k.replace('_', ' ').title() for k, _ in reversed(sorted_fi)]
        feat_vals = [v for _, v in reversed(sorted_fi)]
        
        plt.figure(figsize=(8, 6), dpi=300)
        plt.barh(range(top_k), feat_vals, color='#0d9488', edgecolor='#115e59', height=0.65)
        plt.yticks(range(top_k), feat_labels, fontsize=10, color='#1e293b')
        plt.xlabel('Gini Feature Importance', fontsize=11, labelpad=8, color='#1e293b')
        plt.title(f'Top {top_k} Most Informative Biological Features\n({best_model_name})', fontsize=12, fontweight='bold', pad=12, color='#1e293b')
        plt.grid(axis='x', linestyle=':', alpha=0.6)
        plt.tight_layout()
        fi_path = os.path.join(fig_dir, "feature_importance.png")
        plt.savefig(fi_path)
        plt.close()
        print(f"      [x] Feature importance: {fi_path}")
        
    # Figure 5: Model Comparison Bar Chart
    plt.figure(figsize=(9, 5), dpi=300)
    m_names = list(evaluation_results.keys())
    accs = [evaluation_results[m]["test_accuracy"] for m in m_names]
    recs = [evaluation_results[m]["test_recall"] for m in m_names]
    f1s = [evaluation_results[m]["test_f1"] for m in m_names]
    
    x = np.arange(len(m_names))
    width = 0.25
    plt.bar(x - width, accs, width, label='Accuracy', color='#0f766e', edgecolor='#115e59')
    plt.bar(x, recs, width, label='Pathogenic Recall', color='#0284c7', edgecolor='#0369a1')
    plt.bar(x + width, f1s, width, label='F1-Score', color='#d97706', edgecolor='#b45309')
    
    plt.ylabel('Metric Score (0.0 - 1.0)', fontsize=11, labelpad=8, color='#1e293b')
    plt.title('Benchmark Performance Comparison Across Models', fontsize=12, fontweight='bold', pad=12, color='#1e293b')
    plt.xticks(x, [m.replace(' ', '\n') for m in m_names], fontsize=10, color='#1e293b')
    plt.ylim([0.0, 1.05])
    plt.legend(loc="lower right", frameon=True, fontsize=10)
    plt.grid(axis='y', linestyle=':', alpha=0.6)
    plt.tight_layout()
    mc_path = os.path.join(fig_dir, "model_comparison.png")
    plt.savefig(mc_path)
    plt.close()
    print(f"      [x] Model comparison chart: {mc_path}")
    
    print("\n[+] Training and Evaluation Pipeline Finished Successfully!")
    return best_results

if __name__ == "__main__":
    run_training_pipeline()
