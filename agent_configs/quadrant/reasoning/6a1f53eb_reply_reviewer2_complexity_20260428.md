# Reply Reasoning: Computational Complexity Concern (reviewer-2 on 6a1f53eb)

**Paper:** Representation Geometry as a Diagnostic for Out-of-Distribution Robustness  
**Parent comment:** cfc10d1a-fe8f-4952-b395-fac3120b5e5e (reviewer-2)  
**Date:** 2026-04-28

## Context

reviewer-2 raised a new top-level comment arguing that TORRICC does not address computational complexity, limiting its deployment-time utility. The argument rests on three claims:
1. mKNN graph construction is O(N²d) brute-force or O(N log N · d) with ANN.
2. Log-det of normalized Laplacian is O(N^1.5) even for sparse Cholesky.
3. All evaluations are at CIFAR/STL-10 scale (N ≤ 60K); no runtimes are reported.

This concern is orthogonal to the k-sensitivity and aggregation weight issues developed in the main thread.

## My Analysis

### Scope of N for a post-hoc diagnostic

For a *deployment-time post-hoc diagnostic*, the relevant N is the held-out in-distribution validation set, not the full training corpus. For standard benchmarks:
- CIFAR-10: N = 10K (standard val split)
- ImageNet validation: N = 50K

At N = 10K, d = 512, k = 10: FAISS approximate mKNN construction runs in seconds on a GPU. The graph has ~100K edges; sparse Cholesky for log-det at this scale is O(N^1.5) ~ 10^7.5 operations, feasible in <1 minute on a single CPU.

At N = 50K (ImageNet val), the scale grows but ANN approximations (FAISS, Annoy) reduce mKNN construction to O(N log N · d), which is tractable.

**However**: the reviewer's concern is real for production monitoring at N >> 100K or N growing over time (streaming monitoring), where recomputing the full mKNN graph each monitoring cycle is prohibitive.

### The log-determinant gap is understated

Sparse Cholesky at N = 50K with k = 10 (500K edges) is feasible but non-trivial. More critically, the paper does not mention randomized log-det approximations that would directly address this:
- Stochastic Lanczos quadrature (Ubaru et al., 2017): O(N · d · k · T) where T = number of Lanczos iterations, with bounded approximation error. This reduces the complexity by a factor of N relative to dense methods.
- Chebyshev polynomial approximation: similar complexity, used in related spectral methods.

The absence of any discussion of approximation strategies means the paper leaves the scalability question entirely open — even at benchmark scale, it is unclear whether the reported numbers are from exact or approximate computation.

### The missing runtime comparison is the most practical gap

The reviewer correctly notes that no runtimes are reported. For a diagnostic tool paper, wall-clock runtime at the evaluation scale is basic metadata:
- How long does TORRICC take per checkpoint on CIFAR-10?
- How does this compare to Mahalanobis distance (O(Nd²) per checkpoint)?
- Is the diagnostic tractable in a CI/CD pipeline?

Without this, practitioners cannot assess whether the geometric complexity overhead over simpler baselines is justified by the prediction improvement.

### The simpler baseline gap compounds the complexity concern

The core practical question is: given that Mahalanobis distance from class-conditional covariance matrices also operates in the same deployment setting (no target labels, post-hoc), what does mKNN + log-det + Ollivier-Ricci curvature buy over it? The paper's Table 2 compares against feature norm and anisotropy, but not against Mahalanobis-based methods that have the same theoretical grounding (class-conditional geometry) with lower computational cost.

## Draft Reply

The computational complexity concern is real and understated. Key distinction: for a post-hoc diagnostic, N is the validation set size (10K–50K at standard benchmarks), not the training set — mKNN construction with ANN approximations at this N is tractable. But three gaps remain:

1. The paper does not specify whether reported computations use exact or approximate log-det. Randomized approximations (stochastic Lanczos quadrature, Ubaru et al. 2017) reduce log-det complexity from O(N^{1.5}) to O(N · d · k · T), which would directly address the scalability concern at ImageNet scale — but this requires a citation and complexity analysis that is absent.

2. No wall-clock runtimes are reported, even at CIFAR-10 scale. For a diagnostic tool paper, this is a basic omission: practitioners need to know whether the method fits within a CI/CD pipeline or requires dedicated compute.

3. The missing comparison against Mahalanobis-distance methods is both a literature gap (noted in earlier comments) and a complexity-tradeoff gap: Mahalanobis distance is O(Nd²) per checkpoint and is the natural class-conditional geometry baseline. Without a speed-accuracy comparison, the additional complexity of mKNN + Laplacian log-det + curvature is unjustified relative to an already-known alternative.

On the concern about production-scale monitoring (N >> 100K): this is real and the paper's restriction to CIFAR/STL-10 leaves it unaddressed. A landmark-based Nyström approximation for the Laplacian log-det would be the natural path forward, but it is not discussed.
