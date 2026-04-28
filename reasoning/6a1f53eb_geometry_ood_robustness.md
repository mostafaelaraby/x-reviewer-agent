# Reasoning: Representation Geometry as a Diagnostic for OOD Robustness (6a1f53eb)

**Paper**: Representation Geometry as a Diagnostic for Out-of-Distribution Robustness  
**ArXiv**: 2602.03951  
**Date**: 2026-04-28  
**Reviewer**: quadrant

---

## Four-Lens Analysis

### Lens 1: Citations

- Ollivier (2007) for OR curvature is the correct primary source.
- Ray & Singer (1971) and Lyons (2005) cited for analytic torsion / Matrix-Tree — appropriate.
- CKA baseline: Kornblith et al. (2019) — correct.
- Domain generalization baselines (IRM, SWAD, SWA) properly cited.
- **Gap**: The paper's practical use case — unsupervised label-free OOD performance estimation / checkpoint selection — has a substantial existing literature not cited:
  - Guillory et al. (2021), "Predicting with Confidence on Unseen Distributions" (agreement-based OOD estimation)
  - Garg et al. (2022), "Leveraging Unlabeled Data to Predict Out-of-Distribution Performance"
  - Deng & Zheng (2021), "Are Labels Necessary for Classifier Accuracy Evaluation?"
  These works address essentially the same deployment problem (OOD performance estimation without target labels) using complementary approaches. The paper compares only against low-order representation statistics (CKA, feature norm), not against these OOD-estimation baselines.

### Lens 2: Novelty

The combination of analytic torsion–inspired log-determinant and Ollivier–Ricci curvature applied to class-conditional k-NN graphs for OOD diagnosis is novel. Individual components are well-established (Chung 1997; Ollivier 2007; Topping et al. 2022 for OR curvature in GNNs), but their joint use as predictive signals for checkpoint selection is not established in prior work. 

**Classification: clear-novelty** — genuine methodological contribution, but the comparison set for the practical use case is incomplete.

### Lens 3: Rigor

**Finding A (Table 2): Feature norm outperforms torsion without justification.**
Table 2 reports Spearman ρ correlations: Feature norm ρ = -0.91, Torsion ρ = -0.88, Anisotropy ρ = +0.93. Two baselines (feature norm, anisotropy) exhibit stronger correlations with OOD accuracy than the paper's proposed torsion metric. The paper does not discuss this ordering. If feature norm alone is a stronger predictor, the additional computational overhead of constructing k-NN graphs and computing log-determinants needs to be justified by some other property (e.g., better checkpoint selection, interpretability advantage, or robustness to pathological cases). The selection results in Table 3 do not directly address this, as they report only torsion, curvature, and GeoScore — not a feature-norm-based selector.

**Finding B (Table 6): k-sensitivity undermines practical usability.**
Table 6 shows that the torsion proxy (log det* L) varies dramatically with k: values of -235.4 (k=5), +498.7 (k=10), and +1002.2 (k=15) — a sign flip and a range of ~1237 units across k values. The paper states that "qualitative relationship remains stable," but this instability in absolute values means the metric cannot be reliably compared across training runs without fixing k, and the optimal k is not theoretically motivated. The curvature values also change sign (0.042 → -0.111 → -0.133), further complicating the interpretation that "higher curvature → more robust." If curvature is negative at the "best" checkpoint under certain k choices, the GeoScore formulation (which rewards higher curvature) would select incorrectly.

**Finding C: Architecture scope does not support "across multiple architectures" claim.**
The abstract and contributions claim evaluation "across multiple architectures." ViT-S/16 results are relegated to the Appendix. The main text results are exclusively ResNet-18 on CIFAR-10. For a "diagnostic" framework intended for practical model selection, demonstrating the signal on two vision architectures within the same family is a limited scope. Natural language models, diffusion models, or graph neural networks — contexts where OOD shift is equally problematic — are not addressed.

### Lens 4: Literature

Related Work covers domain generalization (IRM, SWAD, SWA), representation comparison (CKA), and spectral/topological tools adequately.

**Gap**: The practical claim of "unsupervised checkpoint selection under shift" (Sec 4.7) sits in a rich literature on agreement-based and prediction-based OOD performance estimation (Guillory et al. 2021; Garg et al. 2022). These methods achieve label-free OOD performance estimation using disagreement between models or confidence calibration, without any representation geometry computation. The paper should benchmark against these baselines to demonstrate that geometry-based selection adds value beyond simpler proxy measures.

---

## Evidence Quotes

1. **Table 2** (p. 5): "Feature norm −0.91 ... Torsion (logdet) −0.88" — Feature norm has stronger correlation than torsion.

2. **Table 6** (p. 7): "avgpool k=5: log det* L = -235.4 ... avgpool k=10: 498.7 ... avgpool k=15: 1002.2" — torsion values change sign and magnitude dramatically with k.

3. **Section 4.7 / Table 3** (p. 6): "Curvature-only 60 ep060 0.7125" vs. "Oracle 199 ep199 0.8975" — curvature-only selection is 17.5 pp below oracle, exposing single-metric unreliability.

4. **Abstract/Introduction**: Claims "across multiple architectures, training regimes, and corruption benchmarks" — but ViT results are Appendix-only; all main text experiments are ResNet-18.

---

## Overall Assessment

The TORRICC framework is conceptually novel and the geometric motivation is sound. The main concerns are: (a) baseline ordering in Table 2 showing that simpler metrics (feature norm, anisotropy) correlate more strongly with OOD accuracy than torsion, without justification; (b) dramatic k-sensitivity in Table 6 that would require careful per-run tuning in practice; and (c) an absent comparison with the prominent label-free OOD estimation literature. 

**Band: weak-accept** — the diagnostic framework is valuable but the empirical gaps weaken the claims to reliability and practical utility.
