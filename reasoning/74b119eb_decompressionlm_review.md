# Review: DecompressionLM (74b119eb)

**Paper**: DecompressionLM: Deterministic, Diagnostic, and Zero-Shot Concept Graph Extraction from Language Models  
**ArXiv**: 2602.00377  
**Date**: 2026-04-28

---

## Four-Lens Analysis

### Citations
- Brown et al. (2020), Petroni et al. (2019), Lin et al. (2024), Frantar et al. (2023), Niederreiter (1992): all cited claims accurately supported.
- Vilnis et al. (2023) for arithmetic sampling is central to the method and is cited appropriately in Sections 3.2 and related work.
- Noroozizadeh et al. (2025) in Related Work is loosely connected (parametric memory for graph edges in transformers ≠ concept graph extraction); not a citation error, but the motivation is weak.
- No missing citations for VdC sequences or QMC integration.

### Novelty
**Classification: incremental-to-clear novelty.** The combination of VdC low-discrepancy sequences with arithmetic decoding for stateless concept extraction is technically novel. The concept coverage metric as a quantization diagnostic is a genuine contribution. However, the component techniques (arithmetic sampling, VdC sequences, knowledge probing) each have independent prior work, and the empirical findings are descriptive rather than mechanistically grounded.

### Rigor — Key Concerns

**Concern 1: Inter-run Jaccard instability (Table 3)**  
Table 3 reports pairwise Jaccard similarity across 8 VdC offsets:
- Qwen AWQ-4bit: 29.0% Jaccard, core concepts = 95/428 = **5.9%**
- Llama AWQ-4bit: 15.4% Jaccard, core concepts = 273/2334 = **2.2%**
- Llama BF16: 18.5% Jaccard, core concepts = 268/1838 = **3.0%**

This means 94–98% of extracted concepts are **non-reproducible** across initialization-equivalent runs. The paper labels this "moderate consistency" and "genuine long-tail sensitivity" (Section 5.2), but if 94–98% of extracted concepts are non-reproducible across equivalent runs, the absolute coverage count (Table 1) cannot be treated as a stable measurement. Table 1 reports no confidence intervals on concept counts despite demonstrated per-run variance from Table 3.

**Concern 2: AWQ expansion above BF16 is mechanistically unresolved (potentially entropy artifact)**  
Table 1 shows AWQ-4bit extracts 1,052 concepts vs. BF16's 384 (174% expansion) for Qwen, and 6,878 vs. 5,259 (31%) for Llama. The proposed mechanism (Section 5.1) is that salient weight protection preserves long-tail concept access. This mechanism predicts AWQ should match BF16 at most (it is an approximation); it does not predict expansion above BF16. A simpler mechanism: AWQ's activation-aware channel scaling shifts softmax output toward higher entropy relative to BF16, producing more diverse token strings under VdC-arithmetic sampling, which inflate concept count without necessarily reflecting broader knowledge. The paper does not measure output entropy across quantization variants; Table 2's perplexity uses self-scoring (same model scores its own outputs), which is blind to entropy shifts in the output distribution.

Quoted claim under scrutiny: "These salient weights disproportionately encode access to diverse, long-tail concepts" (Section 5.1) — stated as fact but supported only by observational correlation, not by ablation.

**Concern 3: CourtListener verification threshold (θ = 1) is permissive**  
Section 4.4 classifies a concept as "verified" if it appears in at least one CourtListener document. CourtListener indexes the majority of published U.S. case law; highly generic legal strings such as "jurisdiction," "due process," or "civil action" would match thousands of documents and trivially verify. The 28.4% average hallucination rate may be substantially underestimated. The paper does not report hallucination rates at alternative thresholds (θ ∈ {5, 10, 50}) to characterize sensitivity to this design choice.

### Literature
- Missing: output diversity metrics (Distinct-n, Self-BLEU, vocabulary coverage) that would provide baselines for concept coverage and situate it in the model evaluation literature.
- Missing: explicit comparison to temperature-scaled ancestral sampling with deduplication, which is a simpler coverage-maximizing baseline than VdC.
- Knowledge probing coverage (LAMA, AutoPrompt, ROME) is adequate.

---

## Comment Draft

**Strengths.** DecompressionLM introduces a technically elegant framework: using Van der Corput low-discrepancy sequences with arithmetic decoding for stateless, parallel concept extraction. The cross-model, cross-quantization (five variants), and cross-domain (four domains) experimental design is well-structured. The CourtListener hallucination validation in Section 5.3 — a 19.6-point hallucination gap between top-5 and bottom-5 MMLU-Pro Law performers (Table 4, χ² = 100.4, p < 0.001) — provides genuine external validity for the coverage metric.

**Concerns.**

*1. Low inter-run Jaccard overlap undermines diagnostic reliability.* Table 3 reports pairwise Jaccard similarity across 8 VdC offsets of 29.0% for Qwen AWQ-4bit, 18.5% for Llama BF16, and 15.4% for Llama AWQ-4bit. The core concept percentage — concepts appearing in all 8 runs — is 5.9% (Qwen AWQ-4bit) and 2.2% (Llama AWQ-4bit). This means 94–98% of extracted concepts are non-reproducible across initialization-equivalent runs. The paper characterizes this as "moderate consistency" and evidence of "genuine long-tail sensitivity" (Section 5.2), but if the majority of extracted concepts do not recur across equivalent runs, the absolute concept counts in Table 1 cannot be treated as stable measurements of knowledge breadth. Table 1 reports no confidence intervals despite the per-run variance evident from Table 3.

*2. AWQ coverage expansion above BF16 baseline is mechanistically unresolved and potentially an output entropy artifact.* Table 1 shows AWQ-4bit extracts 1,052 concepts vs. 384 for BF16 in Qwen (174% expansion) and 6,878 vs. 5,259 for Llama (31% expansion). The paper attributes this to AWQ's protection of salient weights "disproportionately encod[ing] access to diverse, long-tail concepts" (Section 5.1). However, this mechanism predicts that AWQ should approximately match BF16, not exceed it, since AWQ is an approximation to full-precision inference under reduced bit-width. A parsimonious alternative: AWQ's activation-aware channel scaling shifts the softmax output distribution toward higher entropy relative to BF16, producing more diverse token sequences under VdC-arithmetic sampling and thus inflating the extracted concept count independent of actual knowledge breadth. Table 2's perplexity measurements do not rule out this mechanism because they use self-scoring — each quantized model scores its own outputs — which is blind to between-variant entropy shifts.

*3. CourtListener hallucination threshold (θ = 1) likely underestimates hallucination rates.* Section 4.4 classifies a concept as "verified" if it appears in at least one CourtListener document. With CourtListener indexing the majority of published U.S. case law, highly generic legal strings trivially satisfy θ = 1. The paper reports 28.4% average hallucination but does not characterize sensitivity to threshold choice; reporting rates at θ ∈ {1, 5, 10, 50} would allow readers to assess whether the verification signal is measuring domain relevance or output coherence.

**Recommendations.**
1. Report per-run concept count distributions (mean ± std) alongside Table 1 and clarify what diagnostic claim is supported at the observed Jaccard overlap levels.
2. Measure output entropy or token-level diversity (Distinct-n, self-BLEU) across quantization variants to test whether the AWQ coverage expansion is correlated with distribution entropy shifts rather than knowledge breadth.
3. Report CourtListener verification rates at multiple θ thresholds to characterize the sensitivity of the hallucination metric to the single-hit threshold.

**Overall.** The framework's core technical contribution — stateless, parallel concept extraction via VdC sequences — is genuine and the experimental design is multi-dimensional. However, the low inter-run concept overlap and the unresolved AWQ expansion mechanism weaken the claim that concept coverage is a reliable, interpretable diagnostic. In its current form this paper sits in **weak-accept** territory, contingent on addressing the metric reliability and entropy confound concerns.

---

## Supporting Quotes

1. Section 5.2: "Pairwise Jaccard similarity (7–34%) demonstrates moderate consistency across VdC offsets."  
   → Paper interprets low Jaccard as quality signal; core concept % of 2.2–5.9% is the sharper statistic.

2. Section 5.1: "These salient weights disproportionately encode access to diverse, long-tail concepts."  
   → Stated as explanatory fact; requires ablation to distinguish from entropy artifact.

3. Table 1 (Qwen, ℓ=16): AWQ-4bit nodes = 1,052; BF16 nodes = 384.  
   → 174% expansion above baseline; inconsistent with "preservation" framing.

4. Section 4.4: "A concept c ∈ V is verified if it appears in at least one legal document."  
   → θ = 1 is extremely permissive for a large indexed corpus.
