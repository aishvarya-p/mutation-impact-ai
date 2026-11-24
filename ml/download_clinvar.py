#!/usr/bin/env python3
"""
ClinVar Variant Data Acquisition Script
Mutation Impact AI - NCBI ClinVar Downloader

Streams authentic, peer-reviewed clinical variant records from official NCBI ClinVar:
https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz

Filters:
- Assembly: GRCh38
- High-confidence Clinical Significance:
    - Benign / Likely benign -> Class: Benign
    - Pathogenic / Likely pathogenic -> Class: Pathogenic
- Uses PositionVCF, ReferenceAlleleVCF, AlternateAlleleVCF
- Deduplication by (Chromosome, Position, Ref, Alt)
"""

import os
import sys
import gzip
import json
import time
import argparse
import urllib.request
from datetime import datetime, timezone

CLINVAR_FTP_URL = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz"

def normalize_clinsig(sig_str: str):
    """
    Parses ClinicalSignificance string into binary classification:
    Returns 'Benign', 'Pathogenic', or None if uncertain / conflicting / not provided.
    """
    if not sig_str or sig_str == "-":
        return None
    
    sig_lower = sig_str.lower()
    if "conflicting" in sig_lower or "uncertain" in sig_lower or "not provided" in sig_lower:
        return None
        
    has_benign = "benign" in sig_lower
    has_pathogenic = "pathogenic" in sig_lower
    
    if has_benign and has_pathogenic:
        return None  # conflicting evidence
        
    if has_pathogenic:
        return "Pathogenic"
    if has_benign:
        return "Benign"
        
    return None

def download_clinvar_subset(
    output_path: str = "data/raw/clinvar_raw_variants.tsv",
    target_per_class: int = 10000,
    assembly: str = "GRCh38",
    url: str = CLINVAR_FTP_URL
):
    print(f"[*] Connecting to NCBI ClinVar: {url}", flush=True)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "MutationImpactAI/1.0 (Research Pipeline)"})
    
    try:
        response = urllib.request.urlopen(req, timeout=60)
    except Exception as e:
        print(f"[!] Error connecting to NCBI ClinVar: {e}", flush=True)
        raise
        
    print("[*] Stream connected. Initializing streaming decompression...", flush=True)
    gz_stream = gzip.GzipFile(fileobj=response)
    
    header_line = gz_stream.readline().decode("utf-8").strip()
    if header_line.startswith("#"):
        header_line = header_line[1:]
    header = header_line.split("\t")
    
    col_map = {name: idx for idx, name in enumerate(header)}
    
    # Required columns
    check_cols = ["Chromosome", "ClinicalSignificance", "Assembly", "PositionVCF", "ReferenceAlleleVCF", "AlternateAlleleVCF"]
    for c in check_cols:
        if c not in col_map:
            raise ValueError(f"Required column '{c}' missing from ClinVar header!")
            
    seen_variants = set()
    benign_count = 0
    pathogenic_count = 0
    total_scanned = 0
    
    print(f"[*] Target records per class: {target_per_class} (Total target: {target_per_class * 2})", flush=True)
    print(f"[*] Target Assembly: {assembly}", flush=True)
    
    with open(output_path, "w", encoding="utf-8") as out_f:
        out_f.write("\t".join(["AlleleID", "VariationID", "GeneSymbol", "GeneID", "Type", "Name",
                              "ClinicalSignificance", "Assembly", "Chromosome", "Start",
                              "ReferenceAllele", "AlternateAllele", "ReviewStatus", "NumberSubmitters",
                              "BinaryClass"]) + "\n")
        
        for line_bytes in gz_stream:
            total_scanned += 1
            if total_scanned % 50000 == 0:
                print(f"    Scanned: {total_scanned:,} | Benign: {benign_count:,}/{target_per_class:,} | Pathogenic: {pathogenic_count:,}/{target_per_class:,} ({time.time()-t0:.1f}s)", flush=True)
                
            try:
                line = line_bytes.decode("utf-8").strip()
            except UnicodeDecodeError:
                continue
                
            parts = line.split("\t")
            if len(parts) <= max(col_map.values()):
                continue
                
            # Filter assembly
            if parts[col_map["Assembly"]] != assembly:
                continue
                
            # Filter chromosome
            chrom = parts[col_map["Chromosome"]].replace("chr", "").strip()
            valid_chroms = {str(i) for i in range(1, 23)}.union({"X", "Y", "MT", "M"})
            if chrom not in valid_chroms:
                continue
                
            # VCF position and alleles
            pos = parts[col_map["PositionVCF"]].strip()
            ref = parts[col_map["ReferenceAlleleVCF"]].strip().upper()
            alt = parts[col_map["AlternateAlleleVCF"]].strip().upper()
            
            if not pos or pos == "na" or not ref or not alt or ref == "NA" or alt == "NA" or ref == "-" and alt == "-":
                continue
                
            # Clinical significance mapping
            raw_sig = parts[col_map["ClinicalSignificance"]]
            norm_sig = normalize_clinsig(raw_sig)
            if not norm_sig:
                continue
                
            # Quota check
            if norm_sig == "Benign" and benign_count >= target_per_class:
                continue
            if norm_sig == "Pathogenic" and pathogenic_count >= target_per_class:
                continue
                
            # Deduplication key
            variant_key = f"{chrom}:{pos}:{ref}>{alt}"
            if variant_key in seen_variants:
                continue
            seen_variants.add(variant_key)
            
            # Map into standard names
            allele_id = parts[col_map.get("AlleleID", 0)]
            variation_id = parts[col_map.get("VariationID", 0)] if "VariationID" in col_map else "-"
            gene_symbol = parts[col_map.get("GeneSymbol", 0)]
            gene_id = parts[col_map.get("GeneID", 0)]
            var_type = parts[col_map.get("Type", 0)]
            var_name = parts[col_map.get("Name", 0)]
            rev_status = parts[col_map.get("ReviewStatus", 0)]
            num_submitters = parts[col_map.get("NumberSubmitters", 0)]
            
            row = [
                allele_id, variation_id, gene_symbol, gene_id, var_type, var_name,
                raw_sig, assembly, chrom, pos, ref, alt, rev_status, num_submitters,
                norm_sig
            ]
            out_f.write("\t".join(row) + "\n")
            
            if norm_sig == "Benign":
                benign_count += 1
            else:
                pathogenic_count += 1
                
            if benign_count >= target_per_class and pathogenic_count >= target_per_class:
                break

    duration = time.time() - t0
    total_saved = benign_count + pathogenic_count
    print(f"\n[+] Acquisition Complete!", flush=True)
    print(f"    Total scanned lines: {total_scanned:,}", flush=True)
    print(f"    Total unique records saved: {total_saved:,} (Benign: {benign_count:,}, Pathogenic: {pathogenic_count:,})", flush=True)
    print(f"    Elapsed time: {duration:.2f}s ({duration/60:.2f} min)", flush=True)
    print(f"    Output saved to: {output_path}", flush=True)
    
    metadata = {
        "dataset_name": "NCBI ClinVar Variant Summary GRCh38 Extract",
        "source_url": url,
        "assembly": assembly,
        "download_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "total_records": total_saved,
        "benign_records": benign_count,
        "pathogenic_records": pathogenic_count,
        "target_per_class": target_per_class,
        "filtering_rules": [
            f"Assembly == '{assembly}'",
            "Chromosome in {1..22, X, Y, MT}",
            "Valid PositionVCF, ReferenceAlleleVCF, AlternateAlleleVCF",
            "Unambiguous Benign or Pathogenic clinical significance",
            "Deduplicated by genomic coordinate (chr:pos:ref>alt)"
        ]
    }
    meta_path = os.path.join(os.path.dirname(output_path), "download_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as mf:
        json.dump(metadata, mf, indent=2)
    print(f"    Metadata saved to: {meta_path}", flush=True)
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and filter authentic ClinVar variants.")
    parser.add_argument("--output", default="data/raw/clinvar_raw_variants.tsv", help="Path to save raw TSV")
    parser.add_argument("--target-per-class", type=int, default=10000, help="Number of records per class (total = 2 * N)")
    parser.add_argument("--assembly", default="GRCh38", help="Genome assembly (default: GRCh38)")
    args = parser.parse_args()
    
    download_clinvar_subset(
        output_path=args.output,
        target_per_class=args.target_per_class,
        assembly=args.assembly
    )
