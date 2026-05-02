## Header

- **Title:** Private PoEtry: Private In-Context Learning via Product of Experts
- **Authors:** Anonymous (ICML 2026 submission under double-blind review)
- **Domain tag:** Trustworthy-ML / NLP (privacy-preserving ICL; spans text classification, math, and vision-language modalities)
- **One-line gist:** Reformulates differentially-private in-context learning as a Product-of-Experts ensemble in which each context example contributes a clipped log-probability vector, summed and sampled via the exponential mechanism, yielding higher utility than prior DP-ICL baselines (RNM, Privacy-by-Sampling, synthetic-data) while supporting trivial parallelization.

## Core claims

**Methodological**
- Reformulation of private ICL as a Product-of-Experts (PoE) approximation: `p(y_t | y_<t, x, C_{1:J}) ≈ (1/Z) Π_j p(y_t | y_<t, x, C_j)`, equivalent to summing per-example log-probabilities (Eq. 2–3).
- Algorithm 1 ("PoEtry"): per-token, per-example clipped log-probability sum followed by the exponential mechanism, providing (ε, δ)-DP under the privacy unit of "one differing in-context example" (Theorem 3.1).
- Theoretical convergence result (Theorem 3.4) under a "bounded interaction" assumption (Assumption 3.2): as J → ∞, the PoE distribution converges almost surely to the full-context distribution, at rate O(1/√J) from SLLN plus O(1/J) from the bounded residual.
- Shift from "hard voting" (RNM) to "soft predictions" (clipped log-likelihoods) as the central conceptual move; framed as a form of logit steering connected for the first time to privacy.

**Empirical**
- "More than 30 percentage points on average" accuracy improvement over prior DP-ICL methods at small J (specifically J=4) across AGNews, DBPedia, TREC, GSM8k (Figure 2; abstract).
- To match PoE accuracy, RNM requires roughly 4× as many in-context examples (Figure 2).
- Membership Inference Attack (LiRA-style) confirms ε=1-DP brings AUROC near 0.5 on AGNews/DBpedia/TREC/GSM8k (Table 4).
- Compute cost is comparable to RNM (≈0.8 h vs. 23.8 h for PbS, 6.1 h for synthetic data on AGNews 25-context, single A100, Table 9).

**Artifact**
- No new dataset or benchmark; no model release. Source code is referenced as forked from Tang et al. (2024) but no link visible in the text. The contribution is the algorithm and analysis.

## Methods and experimental setup

**Datasets (5 total)**
- **AGNews** (Zhang et al., 2015) — 4-way news classification.
- **DBPedia** (Zhang et al., 2015) — 14-way entity classification.
- **TREC** (Voorhees & Tice, 2000) — 6-way question categorization.
- **GSM8k** (Cobbe et al., 2021) — grade-school math; reformulated as 10-way classification on the *first digit* of the answer (non-standard metric; 0-shot ≈ 14%, 10% chance).
- **Pseudo-name labelling (VLM)** — 5-way classification over ImageNet (Deng et al., 2009) classes mapped to nonsense labels {Dax, Blicket, Perpo, Slation, Shously}, following Tsimpoukelli et al. (2021).

**Splits / sampling.** Training contexts and queries are sampled randomly (not class-conditional) from the test set. Each accuracy ± standard error is over 25 random seeds × 100 random prompts (text/math) or 2500 random seeds (VLM, with Clopper-Pearson CIs). Setup is reused from Tang et al. (2024) and Zhao et al. (2021).

**Models**
- Primary text/math: **Qwen3-4B** (Team Qwen, 2025); reproduction in **Llama3.1-8B** (Dubey et al., 2024) — Tables 5–6.
- VLM: **Qwen2.5-VL-7B-Instruct** (Wang et al., 2024); reproduction in **InternVL3.5-2B** (Zhu et al., 2025) — Table 7.
- All models frozen; no fine-tuning. Parameter counts not explicitly stated beyond model names.

**Training compute / inference compute.** No training. Inference timing on a single A100 GPU. Wallclock times: PbS 23.8 h (25-ctx), synthetic-data 6.1 h, RNM/PoE 0.8 h (Table 9). Reported figures are for 25 × 100 = 2500 evaluations on AGNews.

**Baselines**
- **Synthetic data** (Tang et al., 2024) — uses synthetic data as a privacy bottleneck, sampled then re-input into the LLM. Privacy unit is per-label; their reported privacy holds against ≈100,000+ examples training set. Marked "Lbl. Priv. ✗" (label-private only).
- **Privacy-by-Sampling / PbS** (Wu et al., 2024) — Poisson-subsamples context and averages noisy outputs.
- **Report-Noisy-Max / RNM** (Wu et al., 2024) — hard-vote thresholded predictions plus noise on counts.
- **Non-private ICL** (∞ ε) — upper bound, no DP.
- **No-context / 0-shot** — lower bound.

**Privacy parameters**
- Text classification, math: **ε = 4**, δ = 10⁻⁵ (chosen to match Tang et al. 2024 / prior implementations).
- VLM: **ε = 1**, δ = 10⁻⁵ (per Hsu et al. 2014; Wood et al. 2018 recommendation).
- MIA: **ε = 1**.
- Privacy unit: full-context (one example differs); contrasted with Tang et al. (2024)'s label-conditional unit which they critique as weaker.

**Method-specific hyperparameters**
- **γ (clipping bound) = 2**, set via a sweep on AGNews/Qwen3 (Figure 4 in Appendix; values exp(−2)≈13.5% to 100% preserved).
- **Group size = 1** for text/math, **= 2** for VLM (grouping defined in Appendix B.2; affects signal-to-noise ratio but not sensitivity). Ablation in App. E shows VLM @ 8 examples: groupsize 1 → 50.6%, groupsize 2 → 77.6%, groupsize 4 → 67.6%.
- **Composition.** Primary experiments use single-token outputs, so no token-level composition is invoked. Algorithm 1's binary-search-on-σ uses Advanced Composition (Kairouz et al., 2015) for multi-token outputs.
- PbS: 100 random subsamples, each included with prob 0.5; PRV accountant via Opacus (Yousefpour et al., 2021).

**Statistical protocol**
- Reported as mean ± standard error over 25 seeds (text/math) or 2500 seeds (VLM with Clopper-Pearson). No formal significance tests (e.g., paired t-tests, multiple-comparison corrections); claims of "significant" gains are visual / standard-error-non-overlap based.

**Evaluation metrics**
- Accuracy (text classification, math first-digit, VLM pseudo-name).
- AUROC for the LiRA-style Membership Inference Attack.
- Mean predictive likelihood l_mean and ℓ∞-norm distance between hard/soft and unclipped vectors (Section 4.1, Appendix C).

**Key tables and figures**
- **Table 1** (Qwen3-4B, ε=4, AGNews/DBPedia/TREC, J∈{8,25}). Headlines: PoE 86.3 / 87.3 / 78.9 (J=8) and 87.0 / 88.0 / 78.8 (J=25); RNM at J=8 collapses to 65.5 / 46.3 / 52.4; PbS J=8: 80.7 / 70.3 / 72.2; synthetic 79.8 / 81.9 / 76.3 (uses 410,000 samples). No-DP upper bound 87.5 / 89.9 / 80.5 (J=8).
- **Table 2** (GSM8k, Qwen3-4B). Non-private 44.2/44.5/46.0 at J=4/8/20; RNM 15.7/20.3/36.5; PoE 37.3/40.9/43.1; 0-shot 14%.
- **Table 3** (VLM pseudo-name, ε=1). PoE 35.1/53.7/78.7 vs. RNM 28.8/39.4/69.8 at J=4/8/20; 0-shot 20%; non-private 89.0/89.1/89.8. Also includes "Soft cond. indep." 82.6/82.7/83.3 and "Hard cond. indep." 76.0/80.7/82.6 (no DP noise — pure independence assumption ablation).
- **Table 4** MIA AUROC: AGNews 60.0→52.9; DBpedia 56.9→49.8; TREC 63.6→53.8; GSM8k 93.9→53.5 (no-DP → ε=1).
- **Table 5** Llama3.1-8B reproduction of Table 1: PoE 85.5/90.8/78.8 at J=8.
- **Table 6** Llama3.1-8B reproduction of GSM8k: PoE 31.0/34.5/36.8 at J=4/8/20.
- **Table 7** InternVL3.5 reproduction of VLM: PoE 67.8/88.5/96.5 at J=4/8/20.
- **Table 8** prompt templates per dataset.
- **Table 9** wall-clock timings (above).
- **Figure 1** schematic of PoE architecture with the medical-data prompt-injection example.
- **Figure 2** average accuracy across AGNews/DBPedia/TREC/GSM8k vs. number of in-context examples (1–32); the source of the "30 pp at J=4" headline.
- **Figure 3** sorted predictive likelihood on GSM8k (10-way) showing power-law-like distribution (top class ≈0.6, second ≈0.18).
- **Figure 4** γ-sweep on AGNews showing γ=2 optimal.
- **Figure 5** VLM evaluation schematic.
- **Figure 6** ROC curves for the MIA across AGNews/DBpedia/TREC/GSM8k.

## Cited claims

| # | Paper claim (paraphrase / quote) | Citation key(s) | Bibliography entry |
|---|---|---|---|
| 1 | "DP training is often impractical … leads to significant degradation in utility" | Kurakin et al., 2022; Raisa et al., 2024 | Kurakin, Song, Chien, Geambasu, Terzis, Thakurta — "Toward training at imagenet scale with differential privacy" arXiv 2201.12328 (2022); Raisa, Jalko, Honkela — "Subsampling is not magic: Why large batch sizes work for differentially private stochastic optimisation" ICML 2024. |
| 2 | ICL works for text classification and translation | Brown et al., 2020 | Brown et al. — "Language models are few-shot learners" NeurIPS 2020. |
| 3 | Many-shot ICL effective for mathematical reasoning | Agarwal et al., 2024 | Agarwal et al. — "Many-shot in-context learning" NeurIPS 2024. |
| 4 | Multimodal frozen LLMs perform few-shot vision-language ICL | Tsimpoukelli et al., 2021 | Tsimpoukelli, Menick, Cabi, Eslami, Vinyals, Hill — "Multimodal few-shot learning with frozen language models" NeurIPS 2021. |
| 5 | "ICL can leak privacy about the input" | Duan et al., 2023b; Choi et al.; Wang et al., 2023 | Duan, Dziedzic, Yaghini, Papernot, Boenisch — "On the privacy risk of in-context learning" ACL 2023; Choi, Cao, Dong, Karimireddy — "ContextLeak" ICML 2025 Workshop on Memorization in Trustworthy Foundation Models; Wang et al. — "DecodingTrust" NeurIPS 2023. |
| 6 | RAG / tool-calling motivation | Lewis et al., 2020; Fan et al., 2025 | Lewis et al. — "Retrieval-augmented generation for knowledge-intensive NLP tasks" NeurIPS 2020; Fan, Ding, Zhang, Mo — "MCPToolBench++" arXiv 2508.07575 (2025). |
| 7 | Synthetic data as privacy bottleneck for ICL | Tang et al., 2024 | Tang, Shin, Inan, Manoel, Mireshghallah, Lin, Gopi, Kulkarni, Sim — "Privacy-preserving in-context learning with differentially private few-shot generation" ICLR 2024. |
| 8 | Genetic-algorithm DP synthetic text generation | Sun et al., 2025 | Sun et al. — "DPGA-TextSyn" ACL 2025. |
| 9 | Privacy-Amplification-by-Subsampling for ICL with thresholded logits | Wu et al., 2024; Balle et al., 2018 | Wu, Panda, Wang, Mittal — "Privacy-preserving in-context learning for large language models" ICLR 2024; Balle, Barthe, Gaboardi — "Privacy amplification by subsampling" NeurIPS 2018. |
| 10 | DP soft-prompt remote tuning | Hong et al., 2024 | Hong, Wang, Zhang, Li, Li, Wang — "DP-OPT" ICLR 2024. |
| 11 | DP prompt learning without backprop | Duan et al., 2023a | Duan, Dziedzic, Papernot, Boenisch — "Flocks of stochastic parrots" NeurIPS 2023. |
| 12 | DP tabular ICL via input perturbation | Carey et al., 2024 | Carey, Bhaila, Edemacu, Wu — "DP-TabICL" IEEE BigData 2024. |
| 13 | Full DP fine-tuning baselines | Abadi et al., 2016; Romijnders & Koskela, 2025; Sinha et al., 2025 | Abadi et al. — "Deep learning with differential privacy" CCS 2016; Romijnders & Koskela — "Convex approximation of two-layer ReLU networks for hidden state DP" NeurIPS 2025; Sinha et al. — "VaultGemma" arXiv 2510.15001 (2025). |
| 14 | Parameter-efficient DP fine-tuning | Yu et al., 2021; Romijnders et al., 2026 | Yu et al. — "Differentially private fine-tuning of language models" ICLR 2021; Romijnders, Laskaridis, Shamsabadi, Haddadi — "Noesis" IASEAI 2026. |
| 15 | DP next-token prediction across LLM ensembles | Flemings et al., 2024 | Flemings, Razaviyayn, Annavaram — "Differentially private next-token prediction of large language models" ACL 2024. |
| 16 | Teacher-ensemble aggregation (PATE) | Papernot et al., 2017 | Papernot, Abadi, Erlingsson, Goodfellow, Talwar — "Semi-supervised knowledge transfer for deep learning from private training data" ICLR 2017. |
| 17 | "Min et al. (2022) — five to fifty samples" framing of practical ICL | Min et al., 2022 | Min, Lyu, Holtzman, Artetxe, Lewis, Hajishirzi, Zettlemoyer — "Rethinking the role of demonstrations" EMNLP 2022. |
| 18 | Logit steering literature | Hiranandani et al., 2025; Liu et al., 2021; Zhao et al., 2024 | Hiranandani, Wu, Mukherjee, Koyejo — "Logits are all we need to adapt closed models" ICML 2025; Liu, Sap, Lu, Swayamdipta, Bhagavatula, Smith, Choi — "DExperts" ACL 2021; Zhao, Brekelmans, Makhzani, Grosse — "Probabilistic inference in language models via twisted sequential Monte Carlo" ICML 2024. |
| 19 | Privacy unit / user-level DP discussion | Chua et al., 2024a | Chua, Ghazi, Huang, Kamath, Kumar, Liu, Manurangsi, Sinha, Zhang — "Mind the privacy unit!" COLM 2024. |
| 20 | DP-SGD subsampling formalism | Chua et al., 2024b | Chua, Ghazi, Kamath, Kumar, Manurangsi, Sinha, Zhang — "How private are DP-SGD implementations?" ICML 2024. |
| 21 | Exponential Mechanism / advanced composition foundations | Dwork & Roth, 2014; Kairouz et al., 2015 | Dwork & Roth — "The algorithmic foundations of differential privacy" TCS 2014; Kairouz, Oh, Viswanath — "The composition theorem for differential privacy" ICML 2015. |
| 22 | LiRA-style membership inference; MIA cannot prove training inclusion | Shokri et al., 2017; Carlini et al., 2021; Chang et al., 2025; Zhang et al., 2025 | Shokri, Stronati, Song, Shmatikov — "Membership inference attacks against machine learning models" S&P 2017; Carlini et al. — "Extracting training data from large language models" USENIX Security 2021; Chang et al. — "Context-aware MIAs against pre-trained LLMs" EMNLP 2025; Zhang, Das, Kamath, Tramèr — "MIAs cannot prove that a model was trained on your data" SaTML 2025. |
| 23 | Label-only MIAs against pre-trained LLMs | He et al., 2025 | He et al. — "Towards label-only membership inference attack against pre-trained large language models" USENIX Security 2025. |
| 24 | Calibrate-before-use prompt setup followed | Zhao et al., 2021 | Zhao, Wallace, Feng, Klein, Singh — "Calibrate before use" ICML 2021. |
| 25 | LLM token distributions follow a power law | Mandelbrot, 1954 | Mandelbrot — "Structure formelle des textes et communication" (1954). |
| 26 | Recommended ε ≤ 1 for meaningful guarantees | Hsu et al., 2014; Wood et al., 2018 | Hsu et al. — "Differential privacy: An economic method for choosing epsilon" CSF 2014; Wood et al. — "Differential privacy: A primer for a non-technical audience" Vanderbilt JETL 2018. |
| 27 | DP has disparate fairness impact | Bagdasaryan et al., 2019; Farrand et al., 2020 | Bagdasaryan, Poursaeed, Shmatikov — "Differential privacy has disparate impact on model accuracy" NeurIPS 2019; Farrand, Mireshghallah, Singh, Trask — NeurIPS 2020 PPML workshop. |
| 28 | "Bulletproof glass" privacy-notice paradox | Brough et al., 2022 | Brough, Norton, Sciarappa, John — "The bulletproof glass effect" Journal of Marketing Research 2022. |
| 29 | Pseudo-name labelling task design / open-ended VLM eval | Tsimpoukelli et al., 2021; Derakhshani et al., 2023 | (above) + Derakhshani, Najdenkoska, Snoek, Worring, Asano — "Self-supervised open-ended classification with small visual language models" arXiv 2310.00500 (2023). |
| 30 | Opacus PRV accountant used for PbS | Yousefpour et al., 2021 | Yousefpour et al. — "Opacus" arXiv 2109.12298 (2021). |

**Stated as well-known but uncited (verification candidates).**
- "Most predictions from the LLM follow a power-law distribution (Mandelbrot, 1954)" — Mandelbrot is cited for the linguistic Zipf-like phenomenon in text, not for LLM predictive distributions specifically; whether the citation supports the LLM-token claim is contestable.
- "ICL is widely used … five to fifty samples" — supported by Brown et al., Agarwal et al., Tsimpoukelli, Min et al., but the "5–50" range is asserted rather than substantiated by any single source.
- "Attention weights to other examples are O(1/J)" (Remark 3.3) — stated as plausible without empirical or theoretical backing or attention-pattern citation.
- The framing of PoE/Heskes-Hinton as the foundation of the algorithm — Hinton 2002 / Heskes 1997 are cited, but the specific approximation that an LLM conditional decomposes as a product over per-example experts is novel to this paper and is not itself derived from those references.

## Related-work positioning

**Section 2 (Related Work) structure.** Organized into four implicit threads:

1. **DP-ICL via synthetic-data bottleneck.** Engaged: Tang et al. (2024); Sun et al. (2025). Stated differential: synthetic-data generation is "computationally costly" and "question-dependent token generation limits its applicability." Privacy unit is also weaker (label-private, not full-context, App. B.3).
2. **DP-ICL via subsampling / hard voting.** Engaged: Wu et al. (2024) for both PbS and RNM. Stated differential: PbS yields "suboptimal accuracy" and RNM "discards key information contained in the logits."
3. **DP prompt tuning / prompt learning.** Engaged: Hong et al. (2024) on remote prompt learning, Duan et al. (2023a) on backprop-free prompt learning, Carey et al. (2024) on input perturbation. Stated differential: these "do not follow the ICL framework and require additional training or optimization."
4. **DP fine-tuning, parameter-efficient DP, ensemble/teacher methods (PATE).** Engaged: Abadi et al. (2016); Romijnders & Koskela (2025); Sinha et al. (2025); Yu et al. (2021); Romijnders et al. (2026); Flemings et al. (2024); Papernot et al. (2017). Stated differential: "still require thousands, if not millions, of data points or even additional public data."
5. **Logit steering.** Hiranandani et al. (2025); Liu et al. (2021); Zhao et al. (2024) — claimed novelty: "first to connect [logit steering] to studying privacy."

**Threads gestured at without follow-through in Related Work.**
- **Membership inference attacks on ICL.** Used in Section 4.4 / Appendix E.2 with citations (Shokri 2017; Carlini 2021; Duan 2023b; Chang 2025; He 2025), but no Related Work paragraph situates the MIA literature.
- **Privacy units / threat-model granularity.** Chua et al. (2024a) on "privacy unit" appears only in the algorithm and Appendix B.3 critique of Tang et al.; not given a Related Work paragraph despite being central to the comparison.
- **Product-of-Experts beyond Hinton/Heskes.** No engagement with subsequent PoE literature (e.g., contrastive divergence variants, neural PoE, or experts-mixture in language modeling).
- **Calibrated/uncertainty-aware ICL.** Zhao et al. (2021) "Calibrate before use" is cited only for the prompt setup; the broader literature on ICL calibration / temperature is not engaged, despite the paper's central claim being that uncertainty in soft predictions is what drives gains.

## Open questions and verification hooks

1. **Significance testing.** The phrase "significantly higher" is used throughout (Tables 1, 2, 3, 5, 6, 7) without any explicit hypothesis test. Standard-error overlap is the implicit criterion. For some entries (e.g., Table 3, J=4: PoE 35.1 ± 1.0 vs. "Hard cond. indep." 76.0 ± 0.9 — a comparison the paper does *not* claim, but which is in the same table; or Table 1 J=25 TREC: PoE 78.8 ± 0.5 vs. RNM 76.7 ± 0.6 — within ~3 SE) the claim of significance is borderline.
2. **GSM8k as a 10-way first-digit classification task.** This is acknowledged as "not standard." It collapses chain-of-thought reasoning into a single-token prediction; the relationship between this metric and conventional GSM8k accuracy (which averages closer to 80–90% for modern models) is undiscussed. The non-private upper bound here is 44–46% on Qwen3-4B (Table 2) and 37–38% on Llama3.1-8B (Table 6), which is far below standard GSM8k scores and may indicate the metric is dominated by digit-distribution noise rather than reasoning.
3. **Privacy-unit comparison with Tang et al. (2024).** The paper repeatedly contrasts its full-context privacy guarantee with Tang et al.'s "label-private" guarantee (Appendix B.3) and notes Tang et al.'s synthetic data is generated from a 100,000- to 410,000-sample base. Whether the head-to-head accuracy comparison in Table 1 is therefore "apples to apples" is contested by the paper itself but not resolved — the synthetic baseline number (79.8 / 81.9 / 76.3) is reported under a *weaker* privacy guarantee against a *much larger* dataset.
4. **PbS settings.** The paper uses 100 random subsamples at sampling probability 0.5 for PbS "due to computational cost" (Appendix E). Whether this matches the configuration in Wu et al. (2024) and whether more samples would improve PbS accuracy is not investigated.
5. **Composition over multiple tokens.** All reported experiments use single-token outputs (Appendix B.1 explicitly states "experiments in Section 4 do not use accounting since the classification predictions have single-token outputs"). The advanced composition over T tokens used in Algorithm 1 is therefore not empirically validated, despite the algorithm being motivated for arbitrary-length generation.
6. **Bounded-interaction assumption (Assumption 3.2).** Stated as "plausible" with three bullet-point intuitions in Remark 3.3, none empirically tested. The paper's Table 3 "Soft cond. indep." / "Hard cond. indep." rows are referenced as supporting the assumption "even without DP noise," but the gap between non-private full-context (89.0 → 89.8) and "Soft cond. indep." (82.6 → 83.3) is 6–7 percentage points — measurable bias rather than vanishing residual.
7. **MIA configuration.** Uses no reference model (justified by "task is novel to the LLM and thus the reference would be uniform"). Whether this assumption holds for AGNews/DBpedia/TREC, which may have appeared in pretraining, is not argued. Result for GSM8k no-DP (AUROC 93.9) is much higher than for the text datasets (56.9–63.6) — unexplained.
8. **MIA includes only ε=1 vs. no-DP.** No comparison against RNM or PbS empirically on the MIA, even though such a comparison would let the privacy-utility trade-off be evaluated jointly.
9. **No ablation of the clipping bound γ across datasets.** γ=2 is fixed by a sweep on AGNews / Qwen3 only (Figure 4). Whether γ=2 is optimal for DBPedia, TREC, GSM8k, or VLM is not verified.
10. **Group-size 2 for VLM only.** Justified post-hoc by "VLM predictions are much better across multiple shots than with a single shot." A counter-experiment on AGNews "led to lower accuracy," but the data behind this claim is not tabulated.
11. **Computational efficiency (Table 9).** PbS at 23.8 h vs. PoE at 0.8 h (≈30× slowdown) — the comparison is contingent on PbS using 100 subsamples; if PbS were tuned for its accuracy ceiling rather than computational floor, the number could change.
12. **No code link in main paper.** The text says they "evaluate their [Tang et al.'s] code with a Qwen3-4B model" (Section 4.2), but no public release URL for this paper's own implementation appears in the main text. Reproducibility footprint depends on appendix detail rather than artifact release.
13. **Author anonymity check.** One reference is unusually self-citing-shaped: Romijnders et al. (2026) "Noesis" (IASEAI 2026) and Romijnders & Koskela (2025) appear in Related Work; if this is the author's own prior work, the anonymization may be at risk. Neutral observation, surfaced for any lens that audits double-blind hygiene.
14. **Choi et al. (year missing).** The citation `(Choi et al.)` in the introduction has no year; the bibliography entry "Choi, J., Cao, S., Dong, X., Karimireddy, S. P. ContextLeak: Auditing leakage in private in-context learning methods. In The Impact of Memorization on Trustworthy Foundation Models: ICML 2025 Workshop" lacks a year field. Verification hook for the citations lens.
15. **"30 percentage point" headline.** In the abstract this is stated without qualification; in Figure 2 the gain is qualified as "at J=4." On DBPedia at J=8, however, PoE 87.3 vs. RNM 46.3 is 41 pp; on AGNews at J=8, PoE 86.3 vs. RNM 65.5 is 21 pp. The averaged figure depends on the dataset/J-range chosen. Direction of effect is robust; the exact "30 pp" number depends on the average chosen.
16. **Theorem 3.1 proof location.** Stated to be in Appendix B.1; the appendix gives an extended argument primarily restating the exponential mechanism's privacy with clipped utilities and quoting the advanced-composition theorem. Whether this constitutes a full formal proof (rather than a proof sketch) is a judgment call.
17. **Mandelbrot 1954 citation.** Cited for "predictions from the LLM follow a power-law distribution," but the cited work concerns text/word-frequency, not next-token predictive distributions. Possibly a misattribution.
