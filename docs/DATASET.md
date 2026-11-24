# ClinVar Variant Dataset Documentation

**Mutation Impact AI — Data Acquisition, Filtering, and Preprocessing Standards**

---

## 1. Primary Source

- **Repository:** National Center for Biotechnology Information (NCBI) ClinVar
- **Public URL:** `https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz`
- **Official Portal:** [https://www.ncbi.nlm.nih.gov/clinvar/](https://www.ncbi.nlm.nih.gov/clinvar/)
- **Release Date:** November 2026 public ClinVar release
- **Genome Reference Build:** GRCh38 (hg38)

---

## 2. Ingestion & Quality Filters

The raw ClinVar database contains over 9.3 million records, including historical assemblies (GRCh37), ambiguous submissions, and somatic variants. The acquisition script (`ml/download_clinvar.py`) streams and applies rigorous filters:

1. **Assembly Alignment:**
   - Retained only variants explicitly mapped to `Assembly == 'GRCh38'`.
2. **Chromosomal Scope:**
   - Standard human chromosomes: Autosomes 1 through 22, Sex Chromosomes X and Y, and Mitochondria (MT/M).
3. **Allele Validity:**
   - Requires non-empty, unambiguous VCF alleles (`ReferenceAlleleVCF` and `AlternateAlleleVCF`).
4. **Clinical Significance Mapping:**
   - **Class 0 (Benign):** Sourced from high-confidence records classified as *"Benign"*, *"Likely benign"*, or *"Benign/Likely benign"*.
   - **Class 1 (Pathogenic):** Sourced from high-confidence records classified as *"Pathogenic"*, *"Likely pathogenic"*, or *"Pathogenic/Likely pathogenic"*.
   - **Excluded:** Any record containing conflicting interpretations, *"Uncertain significance"* (VUS), or missing annotations was discarded to prevent ambiguous training labels.
5. **Deduplication:**
   - ClinVar frequently contains multiple submitter lines for identical genomic loci. Deduplication was performed strictly on the composite coordinate key:
     $$\text{key} = \text{Chromosome} : \text{PositionVCF} : \text{ReferenceAlleleVCF} > \text{AlternateAlleleVCF}$$

---

## 3. Dataset Composition

| Attribute | Verified Count |
| :--- | :--- |
| **Total Cleaned Records** | 20,000 |
| **Benign Variants (Class 0)** | 10,000 (50.0%) |
| **Pathogenic Variants (Class 1)** | 10,000 (50.0%) |
| **Unique Genes Represented** | 3,124 |
| **Training Partition (80%)** | 16,000 variants |
| **Held-out Testing Partition (20%)** | 4,000 variants |

### Top Represented Genes

The dataset exhibits high coverage of clinically sequenced diagnostic panels:
- `TP53` (Tumor Protein p53)
- `BRCA1` & `BRCA2` (Breast Cancer 1 and 2)
- `CFTR` (Cystic Fibrosis Transmembrane Conductance Regulator)
- `LDLR` (Low Density Lipoprotein Receptor)
- `MSH2` & `MLH1` (DNA Mismatch Repair / Lynch Syndrome)
- `SCN5A` & `KCNQ1` (Cardiac Channelopathies / Long QT Syndrome)
- `NF1` & `FBN1` (Neurofibromatosis / Marfan Syndrome)

---

## 4. Feature Dictionary (29 Engineered Predictors)

Target identifiers (`ClinicalSignificance`, `ReviewStatus`, `SubmitterCategories`) are strictly excluded to avoid data leakage. The features utilized:

| Feature Name | Type | Description |
| :--- | :--- | :--- |
| `chrom_num` | Integer (1–25) | Numerical encoding of chromosome (1..22, X=23, Y=24, MT=25) |
| `rel_pos` | Float (0.0–1.0) | Position normalized against GRCh38 chromosome length |
| `log_pos` | Float | Base-10 logarithm of genomic start coordinate |
| `ref_len`, `alt_len` | Integer | Nucleotide sequence length of reference and mutant alleles |
| `length_diff` | Integer | $\Delta = \text{len}(\text{alt}) - \text{len}(\text{ref})$ |
| `is_snv` | Binary (0/1) | Indicates single nucleotide variant ($1 \times 1$ base substitution) |
| `is_deletion` | Binary (0/1) | Indicates genomic sequence deletion ($\Delta < 0$) |
| `is_insertion` | Binary (0/1) | Indicates genomic sequence insertion ($\Delta > 0$) |
| `is_frameshift` | Binary (0/1) | Indicates indel disrupting triplet reading frame ($\|\Delta\| \pmod 3 \neq 0$) |
| `is_inframe` | Binary (0/1) | Indicates in-frame deletion/insertion preserving reading frame |
| `is_transition` | Binary (0/1) | Purine $\leftrightarrow$ Purine ($A \leftrightarrow G$) or Pyrimidine $\leftrightarrow$ Pyrimidine ($C \leftrightarrow T$) |
| `is_transversion` | Binary (0/1) | Purine $\leftrightarrow$ Pyrimidine ($A \leftrightarrow C, A \leftrightarrow T, G \leftrightarrow C, G \leftrightarrow T$) |
| `is_cpg_transition` | Binary (0/1) | $C \to T$ or $G \to A$ transition at spontaneous deamination hotspots |
| `consequence_nonsense` | Binary (0/1) | Premature stop codon creation (stop-gain: `Ter`, `*`) |
| `consequence_frameshift` | Binary (0/1) | Open reading frame disruption (`fs`) |
| `consequence_missense` | Binary (0/1) | Non-synonymous amino acid substitution |
| `consequence_synonymous` | Binary (0/1) | Silent codon substitution with identical amino acid output |
| `consequence_splice` | Binary (0/1) | Canonical splice donor/acceptor site disruption ($\pm 1, 2$ bp) |
| `is_high_impact_lof` | Binary (0/1) | Loss-of-Function indicator (nonsense, frameshift, or splice) |
| `grantham_dist` | Float (0–215) | Grantham amino acid chemical distance matrix score |
| `charge_change` | Integer (0/1/2) | Absolute delta in amino acid charge (+1, 0, -1) |
| `polarity_change` | Binary (0/1) | Polar $\leftrightarrow$ Non-polar property transition |
| `gene_pathogenicity_propensity` | Float (0.0–1.0) | Empirical Bayes smoothed gene pathogenicity prior score |
