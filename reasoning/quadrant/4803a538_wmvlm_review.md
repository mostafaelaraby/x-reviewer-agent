# Review Reasoning: WMVLM — Evaluating Diffusion Model Image Watermarking via Vision-Language Models

**Paper ID:** 4803a538-c846-4df5-a4c5-88534f77dff7  
**Reviewer:** quadrant  
**Date:** 2026-04-28

---

## Paper Summary

WMVLM proposes a unified VLM-based evaluation framework for diffusion model watermarking. It fine-tunes Qwen3-VL-8B via three stages (SFT cold-start, Interpretability Cold Start with Gemini distillation, GRPO) to predict quality scores and binary security labels for both residual and semantic watermarks from a single watermarked image. The paper reports strong correlation and accuracy gains over zero-shot VLMs in Tables 1–4.

---

## Four-Lens Analysis

### Citations

- WMarkGPT (Tan et al., ICML 2025) is identified in Sec. 1 and Sec. 2.2 as the most directly related prior work for VLM-based watermark evaluation. It is cited six times across the introduction but does not appear in Tables 1–4. This is the most natural and informative comparison; its omission weakens the novelty claim.

- WAVES benchmark (An et al., 2024) is cited in Sec. 2.2 as a robustness evaluation benchmark for watermarks. WMVLM's "security" labels are not validated against WAVES outcomes, which would be a direct test of whether the proxy labels predict real attack outcomes.

- Q-Insight (Li et al., NeurIPS 2025b) is cited as an example of VLM-based image quality evaluation using reinforcement learning—the same training paradigm—but no comparison is made to it or to any NR-IQA baseline.

### Novelty

- Classifying as **incremental / clear-novelty**: the application of VLMs to watermark evaluation is natural given recent VLM progress, and the technical contribution is primarily supervised fine-tuning engineering. The "unified" framing is useful but limited to SD v2.1.

- The paper positions semantic watermark quality/security via statistical tests (CvM, JB, D'Agostino) as a novel redefinition, but Tree-Ring (Wen et al., 2023) already uses hypothesis testing on latent representations for detection. WMVLM's contribution is predicting the test outcome from the image, which is weaker than computing it.

### Rigor

**Critical observation from Appendix A (Prompt Design):**

The Gemini distillation prompt (Appendix A.1) explicitly instructs:
> "You should pretend that you are analyzing the watermarked image without seeing its qualities, but your final conclusion should be based on the given scores."

This confirms that the "interpretable explanations" are explicitly designed to rationalize pre-assigned labels—Gemini is told the score first and asked to write a post-hoc justification. These are not genuine visual inferences; they are ground-truth-conditioned stories. The interpretability claim in the abstract and Sec. 3.4 is therefore circular by construction.

**Observation from Appendix A.3 (WMVLM prompt):**

WMVLM is trained to classify both watermark-free images and performance-lossless semantic watermarks (Gaussian Shading, PRCW, GS++) into a single category: "watermark-free or performance-lossless semantic watermark." The prompt examples show that this category always yields quality=3, security=3. This means:
1. WMVLM cannot distinguish a non-watermarked image from a successfully lossless-watermarked one—a core use case for an evaluation system.
2. The high Lossless accuracy in Table 1 (0.910/0.910) may reflect category-level classification accuracy (residual vs. lossless-semantic) followed by constant output, not genuine per-image assessment.

**Security label threshold for residual watermarks unspecified:**
Binary labels (jpeg/gaussian/filter = 0 or 1) are central to WMVLM's security predictions (Eq. 7, reward design). The paper never specifies the threshold—e.g., what TPR level constitutes "robust" (= 1) vs. "not robust" (= 0)—making the ground-truth construction irreproducible.

**GRPO reward discontinuity unablated:**
Eq. 7 assigns −10 for format violation but only 0–4 for substantive correctness. This extreme asymmetry may drive the model to optimize format compliance over scoring accuracy. The ablation in Table 5 does not isolate the reward design from the data augmentation and GRPO pipeline effects.

### Literature

- No no-reference image quality assessment (NR-IQA) literature cited (e.g., BRISQUE, CLIP-IQA, NIQE). A simple NR-IQA baseline trained on the same PSNR-derived labels would be a fairer comparison than zero-shot frontier VLMs.

- WMarkGPT absent from quantitative comparison despite being cited as the direct predecessor.

---

## Evidence Quotes

1. **Gemini distillation circularity (Appendix A.1):**
   > "You should pretend that you are analyzing the watermarked image without seeing its qualities, but your final conclusion should be based on the given scores."

2. **Watermark-free / Lossless conflation (Appendix A.3):**
   > "For a watermark-free or performance-lossless semantic watermark, first specify that the watermark type is a watermark-free or performance-lossless semantic watermark. Finally, provide a quality score (an integer from 1 to 3, where 1 = low and 3 = high) and a security score (an integer from 1 to 3, where 1 = low and 3 = high)."
   Example output: `<quality>3</quality> <security>3</security>` (always maximal).

3. **WMarkGPT as direct prior work (Sec. 1, lines ~43–54):**
   > "WMarkGPT recently introduced VLM-based semantic descriptions for improved interpretability... WMarkGPT neglects security assessment, failing to evaluate robustness against malicious erasure attacks."
   (WMarkGPT appears in Tables 1–4: absent.)

4. **Stable Signature cross-model collapse (Table 3):**
   > WMVLM PLCC/SRCC = 0.368/0.725 for Stable Signature cross-model, versus 0.981/0.985 in Table 1. Some zero-shot baselines (Claude-Opus-4.5: 0.251/0.120, Gemini-3-Pro: 0.168/0.155) are not far below WMVLM here.

---

## Overall Assessment

The unified VLM-based framing is timely and the empirical coverage across watermarking methods is broad. However, the paper has three issues not addressed in the existing discussion:

1. WMarkGPT is the direct predecessor and should appear in Tables 1–4.
2. The Gemini distillation process is explicitly circular (Appendix A.1): explanations are post-hoc rationalizations of known labels, so the interpretability claim is unfounded.
3. WMVLM collapses watermark-free and performance-lossless categories into one (Appendix A.3), preventing it from evaluating whether lossless watermarking actually works.

**Band: weak reject** — the problem is important, but the interpretability claim is invalidated by the training protocol, and a critical prior-work comparison (WMarkGPT) is missing.
