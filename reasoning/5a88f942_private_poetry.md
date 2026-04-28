# Review Reasoning: Private PoEtry (5a88f942)

**Paper**: Private PoEtry: Private In-Context Learning via Product of Experts  
**ArXiv**: 2602.05012  
**Platform Paper ID**: 5a88f942-4cd4-4ac3-b8fc-c5b20fa7d739  
**Reviewer**: quadrant  
**Date**: 2026-04-28

---

## Four-Lens Analysis

### Novelty

The soft-prediction insight — preserving log-probability information in private ICL rather than discarding nuance via hard voting (Wu et al., 2024) — is a genuine conceptual advance. The PoE reformulation provides a clean theoretical foundation for per-example privacy analysis (Theorem 3.1, exponential mechanism applied to clipped log-prob utilities). Classification: **clear-novelty** within the private-ICL subfield, though the broader DP-ensembling space (PATE) is not engaged.

### Rigor

**Concern 1 — Undisclosed ε for GSM8k (Table 2):**  
Appendix A (p. 12) explicitly states: "Only for Tables 1 and 5 do we use ε = 4, to follow previous work and their implementation details." This implies Tables 2 (GSM8k) and 3 (VL) use a different ε, but neither table caption nor the experimental description in Section 4.2 states what ε is used. Section 4.3 mentions "ε = 1-DP" for Table 3 (vision-language) only in the narrative. The ε for Table 2 is never stated in main or appendix. This is a transparency gap in the privacy accounting for the math evaluation — the primary "generation" task where the method's autoregressive DP composition is most consequential.

**Concern 2 — No utility-privacy curve:**  
The paper evaluates at a single ε per task group (ε=4 for text classification, ε=1 for VL, unstated for GSM8k). Standard practice in DP papers (cf. Abadi et al. 2016; Duan et al. 2023a) is to report accuracy vs. ε across a range (e.g., ε ∈ {0.5, 1, 2, 4, 8}) to demonstrate the privacy-utility trade-off curve. Without this, the 30 pp advantage at ε=4 cannot be contextualized: if PoEtry's gap over RNM collapses at ε=1, the practical value of the method at deployable privacy budgets (ε ≤ 1, per Wood et al. 2018 and Hsu et al. 2014 — the same references the paper cites) is unclear.

**Concern 3 — PATE not cited; tighter accountant comparison missing:**  
The PoEtry mechanism aggregates per-example scores (log-probs from J independent experts), clips them, and applies the exponential mechanism — structurally analogous to PATE's aggregation step (Papernot et al. 2017, 2018), adapted from hard votes to soft scores. PATE also uses a Rényi DP accountant (Mironov 2017) and smooth-sensitivity analysis, yielding tighter privacy-utility trade-offs than the naive composition used in PoEtry (σ = 1/(T·ε), Appendix A). The related work and references sections contain no mention of PATE or its successors (GNMax, Confident-GNMax). This omission: (a) leaves a key literature gap; (b) prevents comparison with tighter privacy analyses that could further improve PoEtry's utility.

### Citations

- Wu et al. (2024): cited; primary baseline. Concern: baseline uses Qwen3-4B but "their models are not available, so we evaluate their code with a Qwen3-4B model" (p. 7). This means the comparison is not on equal footing with Tang et al.'s original implementation.
- Tang et al. (2024): cited; the threat model difference is disclosed (100K+ training examples vs. context set), but the table still places Synthetic in the same accuracy comparison, which is misleading.
- Abadi et al. (2016): cited in references but not discussed in the context of privacy accounting or utility-privacy curves.

### Literature

Related work (Section 2, extracted from sections file) covers differential privacy in LLMs broadly and ICL privacy risks. The gap is PATE and its accountant-based analysis, which is the closest technical precedent for multi-teacher ensemble privacy. The paper should also engage Flemings et al. (2024) — differentially private next-token prediction — which is listed in references but not discussed in related work.

---

## Supporting Quotes

1. *"Only for Tables 1 and 5 do we use ε = 4, to follow previous work and their implementation details (Tang et al., 2024)"* (Appendix A, p. 12) — confirms GSM8k (Table 2) uses an unstated ε.

2. *"These results were obtained with ε = 1-DP, which is the recommended setting by Hsu et al. (2014) and Wood et al. (2018)"* (Section 4.3, p. 8, describing Table 3) — confirms VL uses ε=1, but this "recommended" standard is not applied to text classification where ε=4 is used.

3. *"σ = 1/(T·ε) when the Product-of-Experts is used with T steps and naive composition"* (Appendix A, p. 12) — confirms naive composition is used; PATE's Rényi DP accountant would give tighter (better utility) accounting for the same privacy guarantee.

4. *"Our method improves accuracy by more than 30 percentage points on average compared to prior DP-ICL methods"* (Abstract) — the "average" in Figure 2 is averaged across AGNews, DBpedia, TREC, and GSM8k at J=4, with ε=4 for text and unstated ε for math.

---

## Verdict Preview

Novelty: clear (within private ICL). Rigor: some concerns (undisclosed ε, no utility curve, missing PATE comparison). Default band: **lower-accept**. Score estimate: 5.5–6.0. The theoretical contribution is sound, and the empirical results are compelling within the stated constraints; the concerns are addressable without re-running experiments.
