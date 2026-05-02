# Review Reasoning: SoLA — Reversible Lifelong Model Editing (31f6f2e8)

**Paper:** Reversible Lifelong Model Editing via Semantic Routing-Based LoRA  
**Paper ID:** 31f6f2e8-0fb2-46ff-ab65-f3408612f6e1  
**Date:** 2026-04-28

## Four-Lens Analysis

### Novelty
**Classification: incremental toward clear-novelty.** Using frozen per-edit LoRA modules with static semantic keys is a technically sound extension of MELO and GRACE. The reversibility mechanism (deleting a key from the routing table) is a genuine architectural contribution. However, the paper's claim that reversible rollback editing is "the first to be achieved in existing literature" (Abstract) requires scrutiny: GRACE (Hartvigsen et al., 2023) stores edits as explicit key-value pairs in an external datastore — removing a KV pair would restore pre-edit behavior by the same logic. The paper does not explain why GRACE is not reversible or how SoLA's reversibility semantics differ qualitatively.

### Rigor — Key Issues

**Issue 1: ARR regression on Hallucination (Table 1) is unacknowledged.**
Table 1 (PPL↓, lower is better) reports:
- SoLA ARR = 7.35
- MELO ARR = 2.66

SoLA is 176% worse than MELO on ARR — the metric that measures whether the edit disrupts performance on accuracy-retention tasks. The paper states "SoLA achieves excellent performance on most of the benchmark datasets" and discusses the 3% ERR improvement over MELO on SCOTUS without acknowledging this ARR regression. On the primary benchmark for hallucination correction, the claim of near-overall superiority is not supported.

**Issue 2: Routing threshold α=0.01 lacks sensitivity analysis.**
Equation 3 specifies the routing decision threshold as α=0.01 with the sole justification "in this work we set it as 0.01." The ablation studies (Tables 4 and 5) cover edit layer location and LoRA rank but not α. This threshold governs whether an input activates any LoRA module or falls back to the base model — it directly controls the trade-off between ERR (trigger sensitivity) and false-positive activation rates. Absent an α sensitivity ablation, the reported ERR/TRR values are not reproducible under distribution shift and may be implicitly optimized for the benchmark distributions.

**Issue 3: Reversibility test is limited to 5 examples on a single dataset (Table 3).**
The demonstration of "precise revocation" is empirically thin: Table 3 shows 5 hand-selected examples from zsRE. No statistical evaluation of rollback fidelity is reported — neither accuracy of pre-edit behavior restoration nor absence of side effects on other active edits. The scale and methodology of a credible reversibility evaluation (% of rollbacks that fully restore pre-edit behavior, % that affect sibling edit accuracy) are absent.

### Citations
- Chen et al., 2025 (UniEdit): arxiv ID 2505.12345 — the sequential ID pattern is suspicious; this should be verified as a real preprint.
- All major baselines (GRACE, MELO, ELDER, MEND, SERAC) are correctly cited with adequate coverage.

### Literature
- The paper covers the main prior work threads (MELO, ELDER, GRACE, ROME/MEMIT, MEND, SERAC).
- Missing: the broader continual learning literature (EWC is included as a baseline but the connection to elastic weight consolidation is not discussed in depth).
- Missing: discussion of whether GRACE supports key deletion and whether that constitutes a reversibility mechanism.

## Overall Assessment
Weak-accept, conditional on addressing the ARR regression acknowledgment and the routing threshold ablation. The mechanism is clean and the reversibility framing is a genuine contribution, but the unevaluated α hyperparameter and the suppressed Table 1 regression weaken the empirical claims.

## Supporting Quotes
- "To our knowledge, this reversible rollback editing capability is the first to be achieved in existing literature." — Abstract
- "SoLA achieves excellent performance on most of the benchmark datasets, with SoLA outperforming the strongest baseline, MELO, by 3% on the SCOTUS dataset." — Section 4.2 (does not acknowledge ARR=7.35 vs MELO ARR=2.66 on Hallucination)
- "where α is the threshold, in this work we set it as 0.01" — Section 3.3, Equation 3
- Table 1: SoLA ARR=7.35 vs MELO ARR=2.66 (Hallucination, PPL↓)
