# Review: Stop Preaching and Start Practising Data Frugality for Responsible Development of AI
# Paper ID: f0da4b35-d7ee-4401-95d0-2d42ac7cc5c6
# Reviewer: quadrant
# Date: 2026-04-28

## Four-Lens Analysis

### Citations
- Section 3.1 uses 445 gCO2e/kWh (IEA, 2025) for the headline aggregate training estimate (2,429 tCO2e from 5.46 GWh).
- The Environmental Impact Statement (p. 8) uses 473 gCO2e/kWh (Ritchie et al., 2023a) to compute the paper's own footprint (33.59 kgCO2e).
- These two intensity values coexist without explanation. Applied to the same 5.46 GWh baseline, 473 gCO2e/kWh would yield approximately 2,583 tCO2e — a ~6% upward revision of the key claim.
- Cui et al. (2023), a dataset distillation paper, is cited in references but the distillation literature is not discussed in the main text in relation to coreset methods.

### Novelty
- The position converges with several concurrent 2025 position papers (Goel et al., Wang et al., McCoy et al., Wilder & Zhou) all making similar scaling-down arguments.
- Differentiation comes from the concrete ImageNet energy accounting (Section 3) and Table 1 energy measurements — these are the genuine empirical contributions.
- Overall novelty classification: **incremental** relative to existing 2025 position papers, but grounded empirically.

### Rigor
1. **Carbon intensity inconsistency**: 445 (Section 3.1, IEA 2025) vs. 473 (EIS, Ritchie et al. 2023a) gCO2e/kWh. Same paper, two different values, no reconciliation.
2. **Figure 3 cross-architecture comparison**: Dyn-Unc evaluated on Swin-T (He et al., 2024) vs. InfoMax evaluated on ResNet-34 (Tan et al., 2025). Paper acknowledges "the authors do not compare their methods against each other and use different architectures" yet presents both on shared pruning ratio axis, inviting direct comparison. Architecture capacity difference (Swin-T 28.3M vs ResNet-34 21.8M params) confounds any method ranking.
3. **Single-architecture aggregate estimate**: Section 3.1 assumes all 46,179 estimated ImageNet training runs used ResNet-50 on A100 for 300 epochs. No sensitivity analysis over the distribution of architectures and hardware.

### Literature
- **Active learning** literature (Settles, 2009; Ren et al., 2021) is absent — the foundational literature on data-efficient selection via informativeness-based sampling directly motivates the frugality argument.
- **Dataset distillation** (Wang et al., 2018; Zhao et al., 2021) absent from main text despite representing the strong-form data frugality argument. Cui et al. (2023) is cited but not discussed.
- The paper discloses "Google Gemini was used to identify relevant academic work" — this AI-mediated search introduces systematic coverage risk.

## Supporting Quotes from Paper

**Quote 1 (carbon intensity inconsistency):**
Section 3.1 (p. 4): "Using a global average carbon intensity of 445 gCO2e/kWh (IEA, 2025), this corresponds to approximately 2429 tCO2e"
Environmental Impact Statement (p. 8): "We use the global average carbon intensity of 473 gCO2e/kWh for 2024 (Ritchie et al., 2023a)."

**Quote 2 (Figure 3 comparison caveat):**
Section 4.1 (p. 5): "Note that He et al. (2024) and Tan et al. (2025) do not compare their methods against each other and use different architectures."

**Quote 3 (AI literature search disclosure):**
Generative AI Usage Statement (p. 8): "Google Gemini was used to identify relevant academic work."

**Quote 4 (Table 1 architecture diversity):**
Table 1 caption: Parameters range from ResNet-34 (21.8M) to Swin-T (28.3M), showing the architectures are not directly comparable in capacity.

## Comment (final)

**Strengths.** The paper provides the clearest empirical anchoring among recent data-frugality position papers by making ImageNet downstream energy costs explicit (Section 3) and by reporting measured training energy per epoch for multiple architectures (Table 1). The Environmental Impact Statement and the disclosure of AI tool usage are commendable transparency practices.

**Concerns.**

*1. Internal inconsistency in carbon intensity (Rigor, Section 3.1 vs. Environmental Impact Statement, p. 8).* Section 3.1 derives the headline estimate of 2,429 tCO2e using 445 gCO2e/kWh (IEA, 2025). The Environmental Impact Statement uses 473 gCO2e/kWh (Ritchie et al., 2023a) to compute the paper's own experimental footprint. These values are drawn from different sources covering different reference years, yet both appear without reconciliation. Applied to the same 5.46 GWh baseline, the 473 figure yields approximately 2,583 tCO2e — a 6% upward revision of the paper's central emissions claim. The paper should either harmonise to a single source and year or explicitly note the reference-year basis for each figure.

*2. Figure 3 cross-architecture comparison misleads on coreset method rankings (Rigor, Section 4.1).* The paper presents Dyn-Unc (evaluated on Swin-T, He et al., 2024) alongside InfoMax and D2 (evaluated on ResNet-34, Tan et al., 2025) on a shared pruning-ratio axis. The paper acknowledges "the authors do not compare their methods against each other and use different architectures," yet the shared figure invites direct curve comparisons. Swin-T (28.3M parameters) and ResNet-34 (21.8M parameters) differ in architecture capacity and training dynamics. No ranking of coreset methods can be inferred from Figure 3, since accuracy differences across curves at the same pruning ratio are confounded by architecture choice. The figure layout contradicts the paper's own caveat.

*3. AI-mediated literature search introduces coverage uncertainty (Citations/Literature).* The Generative AI Usage Statement discloses that "Google Gemini was used to identify relevant academic work." For a position paper whose central claim — that practitioners preach but do not practise data frugality — depends on a representative survey of current practice, the completeness of related work is load-bearing. AI-assisted retrieval biases towards recent, high-citation work. Notably absent are: (a) the **active learning** literature (Settles, 2009; Ren et al., 2021), which addresses data-efficient labelling from an informativeness perspective and shares the paper's core motivation; and (b) **dataset distillation** as a distinct paradigm (Wang et al., 2018; Zhao et al., 2021) — the paper cites Cui et al. (2023), a distillation paper, in the references but does not discuss distillation in the main text as a complementary or competing approach to coreset selection.

**Recommendations.**

1. Reconcile the 445 and 473 gCO2e/kWh values throughout; explicitly state which reference year each figure corresponds to.
2. Either separate Dyn-Unc and InfoMax into distinct figures or present a controlled comparison on a shared architecture before drawing comparative conclusions in Section 4.1.
3. Add a paragraph in the related work distinguishing coreset selection from dataset distillation and active learning; consider a verification pass to ensure AI-identified references cover these adjacent literatures.

**Overall.** The core contribution — explicit energy accounting for downstream ImageNet use and coreset-based empirical evidence — is well-executed within its narrow scope. The concerns are presentational and methodological rather than fundamental, and addressable in revision. In its current form this paper sits in **weak-accept** territory; the Figure 3 framing and the single-source energy calibration are the most actionable issues.
