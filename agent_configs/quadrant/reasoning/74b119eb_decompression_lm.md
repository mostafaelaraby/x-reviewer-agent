# Review Reasoning: DecompressionLM (74b119eb)

**Paper:** DecompressionLM: Deterministic, Diagnostic, and Zero-Shot Concept Graph Extraction from Language Models  
**Paper ID:** 74b119eb-aaed-4f9d-9ba4-6cec0d5eff72  
**Date:** 2026-04-28

## Four-Lens Analysis

### Novelty
**Classification: clear-novelty (incremental toward clear).** Using Van der Corput low-discrepancy sequences with arithmetic decoding for stateless concept graph extraction is technically novel. The combination of VdC sampling + arithmetic decoding + parallel concept graph extraction is new. The concept coverage metric as a quantization diagnostic is a genuine contribution. However, VdC sequences and arithmetic decoding are individually well-established; the novelty is in their application.

### Rigor — Key Issues

**Issue 1: Perplexity self-scoring design (Table 2)**  
The paper's central claim is that "concept coverage and perplexity are partially decoupled." Table 2 tests this by computing perplexity of model-generated explanations. Critically, the same quantized model acts as both generator (generating explanations of sampled concepts) and scorer (computing perplexity of those explanations under its own distribution). Under AWQ-4bit, which shifts the output distribution toward more diverse outputs (Table 1), the perplexity is trivially near-baseline because the model is scoring its own outputs — any model is well-calibrated to its own generation distribution. The appropriate test would compute perplexity of all configurations under a fixed BF16 reference model. The self-referential design cannot separate "the distributions are equivalent" from "each model is self-consistent."

Quoted claim: "mean/median perplexity remains within a narrow range across quantization variants in each domain, even when earlier sections report large coverage expansion (e.g., AWQ) or collapse (e.g., GPTQ-Int4)" (Section 5.1).

**Issue 2: VdC advantage over ancestral sampling not empirically validated**  
The paper motivates VdC by theoretical properties (Eq. 7, D*_N = O(log N / N) vs. O(N^{-1/2}) for i.i.d. sampling) but never directly compares concept coverage of VdC vs. standard ancestral sampling at the same N. Table 3 shows moderate Jaccard similarity (7–34%) across VdC offsets — this validates robustness to initialization, but does not show VdC outperforms i.i.d. in coverage. Without this comparison, the VdC contribution is theoretical; the empirical results could equally follow from plain ancestral sampling.

**Issue 3: External validation restricted to US Law domain**  
Corpus-grounded hallucination validation (Section 5.3) uses CourtListener, which indexes US legal documents. For Git, Radiology, and FAA domains (Table 1), there is no external ground-truth check. AWQ's 143% Git coverage, 212% Radiology coverage, and 156% FAA coverage (vs. BF16) are unvalidated for factual accuracy. High concept counts in these domains could reflect extraction pipeline artifacts (e.g., repetitive near-duplicate concepts that survive fuzzy merging) rather than genuine knowledge breadth.

**Issue 4: AWQ mechanism hypothesis**  
"Salient weights disproportionately encode access to diverse, long-tail concepts" (Section 5.1) is stated as explanation but not ablated. The alternative (AWQ's activation-weighted rescaling shifts the output distribution rather than preserving specific knowledge) is not ruled out. Mind Changer [54f10712] has flagged this; I concur but prioritize it below the perplexity design issue.

### Citations
- Core citations are appropriate: Petroni et al. (2019) for LAMA, Holtzman et al. (2020) for degeneration, Vilnis et al. (2023) for arithmetic coding, Lin et al. (2024) for AWQ.
- The negative FreqCorr result for Llama-3-Smaug (Table 4) is attributed to "aggressive fine-tuning or merging" without citation or ablation.
- No citation for the claim that CourtListener indexes "the majority of published U.S. case law" — this should be verifiable but is unsourced.

### Literature
- Related Work covers knowledge probing, decoding strategies, and quantization adequately.
- Missing: evaluation of knowledge breadth via generation diversity metrics (SELF-BLEU, entropy-based), and knowledge graph extraction from LLMs (REBEL, ATLOP) which represent the closest alternative extraction framework.

## Overall Assessment
Weak-accept. The perplexity-coverage decoupling and hallucination-benchmark correlation are genuine findings. However, the self-referential perplexity design (Issue 1) weakens the primary empirical claim, and the VdC contribution lacks an empirical comparison to simpler baselines.

## Supporting Quotes
- "mean/median perplexity remains within a narrow range across quantization variants in each domain, even when earlier sections report large coverage expansion (e.g., AWQ) or collapse (e.g., GPTQ-Int4)" — Section 5.1
- "the same quantized model acts as generator and scorer" (implied by design description in Section 4.4, Table 2 caption: "perplexity of the generated explanation under the same model")
- "Pairwise Jaccard similarity (7–34%) demonstrates moderate consistency across VdC offsets" — Section 5.2
- "corpus-grounded validation" limited to CourtListener / US Law (Sections 4.4 and 5.3)
