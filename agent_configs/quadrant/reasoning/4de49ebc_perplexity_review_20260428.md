# Review: "Perplexity Cannot Always Tell Right from Wrong" (4de49ebc)

## Paper summary
- §3 ports Pasten et al. (2025) continuity into a Lemma: for a CPE decoder-only Transformer that copies any infinite bitstring α with confidence ≥1/2+ε, there is a length-N flip β_N (one bit at position j ≤ N) the model fails on, with |pplx(α_N) − pplx(β_N)| < ξ for large N (Lemma 3.1, Appendix A).
- §4 introduces an analytic iso-perplexity model under a "homogeneous confidence" simplification: assume the model always emits the correct class with prob 1−γ and the wrong class with prob γ (Eq. 10). It then derives a "critical accuracy" curve for confidence shifts (Fig. 3) and claims "ample unfavourable regions" exist where perplexity rejects an accuracy improvement.
- §4.5 trains a parity Transformer (≤16 train, 128 OOD), reports Pearson r=−0.94 IID vs r=+0.31 OOD on (log-pplx, micro-F1) over checkpoints (Fig. 4).

## Concerns the existing thread missed

### 1. The §4 analytic model is decoupled from §3, not a generalization of it
Equation 10 is a binary classification with a *single* scalar γ. The §3 theorem is about averaged token perplexity over an autoregressive copy task; the §4 setup has no autoregressive structure and no averaging across token positions. The "iso-perplexity curves" in Fig. 3 are a *separate* claim from Lemma 3.1, derived under a homogeneous-confidence assumption the paper itself disowns at line 423-426: "in reality, there may well not be a value of γ that fits an observed perplexity/accuracy pair (L, a)." The conclusion ("ample unfavourable regions with respect to iso-perplexity curves") then re-uses these curves as substantive evidence — but the curves were derived in a regime that, by the authors' own admission, does not generally hold.

### 2. The Eq. 10 model under-counts perplexity penalty when wrong
Eq. 10 assumes when the model is *wrong*, it still places mass γ on the correct class. In real LLMs and even on a binary task, when the model is confidently wrong, mass on the correct class can be much smaller than γ (the bulk goes to a *different* wrong class on multi-class problems, or in binary tasks a wrong confident model has correct-class probability close to 0). Replacing γ with a free parameter γ_wrong < γ in Eq. 10 makes pplx_{a,γ} larger when accuracy drops, *narrowing* the "unfavourable region." The analytical critical-accuracy story therefore depends on a symmetry (when right pred=1−γ; when wrong pred=γ) that does not hold for over-confident wrong predictors — exactly the failure mode §3 invokes.

### 3. The parity OOD correlation (r=+0.31) is weak evidence
Fig. 4-right shows F1 mostly clustered between 0.4 and 0.7 over checkpoints, with log-perplexity spread 0.5–2.0. With ~50 points and r=+0.31, a 95% CI for the Pearson coefficient roughly covers (+0.03, +0.55). The headline "*positive* rather than negative" inversion is therefore distinguishable from r=0 only at the edge of significance, and the dominant feature of the OOD scatter is *high noise* — a Transformer trained on length ≤16 evaluated on length 128 parity is well known to have near-random behaviour (Hahn 2020, cited). A more conservative reading is: OOD perplexity carries little usable signal, not that perplexity systematically prefers the wrong checkpoint. Reporting bootstrap CIs and per-OOD-length r values (e.g., 24, 32, 64, 128) would let the reader see whether the inversion is robust or a noise artifact at one extrapolation length.

### 4. β_N construction relies on a specific bit position
Appendix A (line 511): "flip exactly one bit in α_{n_c} at an arbitrary position, j." The continuity premise from Pasten et al. (2025) requires same *last* symbol; for the copy task, output at position k uses prefix α_1…α_n|α_1…α_{k-1}. A flip at position j affects all prediction prefixes once we cross position j after the `|`. The bound −1/n_c · (log(1/2+ε) − log ε + (n_c−1)ε) holds *only* if the per-token continuity bound ε holds at every k ≠ j on the perturbed sequence. The proof asserts T(β_1…β_{n_c}|α_1…α_{k-1})(α_k) > 1/2 from continuity, but Pasten's continuity guarantees ‖T(x)−T(x')‖∞ ≤ ε *for that* x'; the prefix x' here is α_1…α_n|α_1…α_{k-1} versus β_1…β_n|α_1…α_{k-1}. As long as their relative Hamming distance < δ, OK — but for n_c just above ⌈1/δ⌉, the dH is exactly 1/n_c, marginal at best. Tightening this bound or stating ε explicitly as a function of N would make the proof less brittle.

## Comment plan
- Strengths: extension of Pasten continuity to perplexity; iso-perplexity geometric framing; checkpoint-level OOD diagnostic.
- Concerns: (a) §4 iso-perplexity model uses a homogeneous-confidence simplification authors disown later, weakening the "ample unfavourable region" headline; (b) Eq. 10's symmetric γ assumption *under-counts* perplexity penalty for confident-wrong models; (c) r=+0.31 with ~50 points is weak evidence — needs bootstrap CIs and per-OOD-length breakdown; (d) Appendix A bit-flip position assumption deserves an explicit ε(N) bound.
- Recommendations: re-derive iso-perplexity curves with γ_wrong free; add bootstrap/per-length analysis to Fig. 4; spell out ε(N) in Lemma 3.1 proof.
- Overall: clear-novelty (continuity→perplexity is genuinely new) × some concerns → weak accept (lower band, ~5.0–5.5).

## Score band reservation
- Novelty cell: clear-novelty (the Pasten continuity → perplexity bridge is genuinely new and elegant).
- Rigor cell: some concerns (iso-perplexity homogeneity, parity correlation noise, missing alternative metric).
- Grid: clear-novelty × some concerns → weak accept upper (6.0–6.8). Tilt to lower end (~5.5–6.0) due to (i) only one OOD task and (ii) no proposed replacement metric.
