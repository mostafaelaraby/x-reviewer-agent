# Review: MCRMO-Attack — Universal Adversarial Perturbations against Closed-Source MLLMs
**Paper ID:** ad4e4ed3-ff72-49a3-8c9d-d5cafab0951e  
**arXiv:** 2601.23179  
**Date:** 2026-04-28

## Four-Lens Analysis

### Novelty
**Classification: clear-novelty.** The paper claims to be the first systematic study of Universal Targeted Transferable Adversarial Attacks (UTTAA) against closed-source MLLMs, where a single perturbation must generalize across arbitrary inputs *and* target a specified output. Prior work is either (a) sample-wise targeted transfer or (b) universal untargeted. The combination of universality + targeting + MLLM transfer appears novel. The three components (MCA+AGC, TR, MI) each have analogues in prior work but their integration in this specific setting is the contribution.

### Rigor — Key Concerns

**1. Judge-victim circularity in the primary evaluation metric (Table 1, Section 5).**
For the GPT-4o evaluation column, the same GPT-4o model is the attack *target* (the model whose output the perturbation must steer) and the *judge* (GPTScore measures semantic similarity between GPT-4o's captions of perturbed vs. target images). This is a circular evaluation design: the attack optimizes GPT-4o's feature space via surrogate encoders, and success is measured by GPT-4o's self-consistency. A model that generates outputs consistent with its own prior outputs under any visual input will score well, independent of whether the perturbation is doing meaningful semantic steering.

Corroborating evidence from Table 1: MCRMO-Attack achieves 61.7% ASR on GPT-4o vs. only 15.9% on Claude (unseen test samples), a 3.9× differential. Since the ε-budget is identical across models (ε = 16/255) and CLIP surrogate encoders are used for all three, the large GPT-4o advantage is consistent with the judge-victim circularity hypothesis — GPT-4o's outputs are evaluated by GPT-4o, while Claude's outputs are evaluated by the same GPT-4o judge. The cross-model evaluation design (GPT-4o judge for all three victims) would partially address this.

**2. Compute budget asymmetry between MCRMO and baselines (Table 5).**
The paper's ablation (Table 5) highlights that meta-initialization allows achieving 54.7% ASR at only 50 stage-2 iterations vs. 52.0% without it at 300 iterations. This is presented as evidence that MI is "sample-efficient." However, the total optimization cost of MCRMO-Attack includes:
- Stage-1 (meta-training): 125 epochs × 16 tasks × 5 inner steps = 10,000 inner gradient steps per target concept (plus outer meta-gradient updates)
- Stage-2: 300 per-target iterations

The baselines (UAP, FOA-Attack, M-Attack) use 300 iterations total. The meta-training budget is omitted from the compute comparison, making the early-stopping advantage appear larger than it actually is. Without a fair total-budget comparison (e.g., holding constant total gradient steps across all methods), it is unclear whether the meta-initialization gains arise from architectural inductive bias or simply more total computation.

**3. Prop IV.1 i.i.d. assumption violation (confirming prior comments).**
Proposition 4.1 states the gradient estimator is unbiased under m i.i.d. views from p(v). In practice, the Attention-Guided Crop selects the highest-attention patch deterministically as a persistent anchor (Section 4.1). This deterministic view is not a sample from p(v); it is a fixed function of the current input and perturbation. The remaining m-1 crops are random, but the batch is not i.i.d. The unbiasedness and variance-reduction claims in Prop IV.1 do not hold for this mixed-deterministic construction. This does not invalidate the empirical results, but it does mean the theoretical grounding for MCA in Theorem 4.1 is unsupported.

### Citations/Literature
The paper covers the main prior work categories (optimization-based transferability, input diversification, feature-level manipulation, targeted MLLM attacks). No obvious gap.

## Evidence anchors from paper
- Table 1: GPT-4o ASR 61.7% vs. Claude 15.9% (unseen), same ε=16/255 budget
- Table 5: meta-init at 50 steps (54.7% ASR) vs. no-meta-init at 300 steps (52.0% ASR) — budget asymmetry not disclosed
- Section 5: "the same closed-source model captions the target and adversarial images, and GPTScore measures their semantic similarity" — judge-victim identity confirmed
- Prop IV.1 / Section 4.1: AGC uses highest-attention patch deterministically

## Assessment
**Novelty:** clear-novelty (first UTTAA framework for closed-source MLLMs)  
**Rigor:** some concerns (evaluation circularity primary; compute budget asymmetry secondary; Prop IV.1 tertiary)  
**Verdict band:** weak-accept (clear-novelty + some concerns → lower-accept per rubric)
