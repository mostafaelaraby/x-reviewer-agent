# Review Reasoning: FHAIM — Fully Homomorphic AIM For Private Synthetic Data Generation

**Paper:** FHAIM: Fully Homomorphic AIM For Private Synthetic Data Generation  
**Paper ID:** 79791abb-515e-43c9-b349-e34d7da163c9  
**arXiv:** 2602.05838  
**Date:** 2026-04-28

## Four-Lens Analysis

### Novelty
- **Classification:** clear-novelty (engineering-level)
- The central contribution — running AIM's adaptive marginal selection loop inside CKKS-encrypted arithmetic — is genuinely new. No prior work implements a full adaptive DP synthesis mechanism under FHE for a single untrusted server.
- The squared L2 norm substitution is the key design decision: CKKS's multiplicative-depth budget makes L1 (|x|) approximation via high-degree Chebyshev polynomials expensive and numerically unstable, while squaring requires only one multiplication level. This is a principled engineering choice with clear motivation.
- However, the individual components (CKKS, AIM, Private-PGM) are all established. The novelty is in their combination and the L2 adaptation.

### Rigor
**Gap 1 — Missing MPC baselines:**
CaPS (Cheng et al., 2024, arXiv:2402.08614) and MPC-MWEM directly address privacy-preserving synthetic data generation using MPC and are the natural empirical competitors. The paper's positioning argument — that FHE avoids MPC's multiple non-colluding parties — is theoretical; without empirical runtime and utility comparison to CaPS, the practical tradeoff is unsubstantiated.

**Gap 2 — L2 norm changes AIM's selection behavior:**
AIM's quality score uses L1 norm: |q(D) - q(x)|. FHAIM replaces it with squared L2: ||q(D) - q(x)||². These have different selection properties under the exponential mechanism. Squared L2 quadratically upweights marginals with large concentrated errors and relatively suppresses marginals with many small distributed errors. The convergence proof for AIM was derived under L1; no new convergence analysis is provided for the L2 variant. The ablation (Table 3) only shows utility values — it does not examine whether the adaptive selection path converges similarly or differently.

**Gap 3 — CKKS precision loss and DP fidelity:**
CKKS is an *approximate* FHE scheme — ciphertext operations introduce bounded floating-point-like precision errors. The DP guarantee requires that the homomorphically computed noisy marginals have an effective noise distribution that matches the intended Gaussian(0, σ²). When encrypted noise (pre-sampled by the data holder) is added homomorphically to encrypted marginals, CKKS introduces an additive precision error ε_CKKS per operation. The paper provides a formal DP sketch but does not bound the impact of accumulated CKKS precision errors on the effective privacy parameter ε_DP. This is the critical unresolved question for practical deployment: does claimed (ε, δ) hold under CKKS-approximate arithmetic?

**Gap 4 — No statistical significance testing:**
All utility results (Tables 1, 2) are single-point estimates from a single seed. No confidence intervals, no standard deviation across seeds, no significance testing. For a prototype system with known floating-point precision sensitivity, result variance matters.

### Citations
- CaPS (arXiv:2402.08614, 2024) is not cited in the paper despite being a directly relevant 2024 MPC-based competitor. This is the most significant literature gap.
- Private-PGM (McKenna et al., NeurIPS 2019, arXiv:2108.04978) is the direct predecessor and should be cited; the existing comments note it is underpositioned.
- "Fast Private Adaptive Query Answering" (arXiv:2602.05674, 2026) is concurrent work in the same adaptive-marginal space; inclusion in related work is appropriate.

### Literature
- The Related Work does not discuss MPC-based SDG alternatives (CaPS, MPC-MWEM). Given the paper's stated positioning against MPC, omitting these is a significant gap.
- AIM (McKenna et al., 2022, arXiv:2201.12677) is the direct technical ancestor; its L1-based convergence analysis is the baseline the paper departs from.

## Key Supporting Evidence for Comment
1. CKKS is approximate arithmetic (standard CKKS literature; Cheon et al. 2017)
2. AIM quality score: L1 norm |q(D) - q(x)| (McKenna et al. 2022, Algorithm 1)
3. FHAIM quality score: squared L2 ||q(D) - q(x)||² (FHAIM paper, Section 3)
4. CaPS: arXiv:2402.08614 — collaborative DP synthetic data via MPC, 2024

## Verdict Assessment (preliminary)
- Novelty: clear-novelty
- Rigor: some concerns (missing MPC comparison, L2 convergence, CKKS DP fidelity)
- Default band: lower-accept / weak-accept range (5.0–6.99)
- The prototype demonstration is convincing for moderate-scale data; the unresolved DP fidelity question is the most serious blocker.
