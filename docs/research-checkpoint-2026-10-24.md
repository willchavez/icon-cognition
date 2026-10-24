# Research checkpoint · October 24, 2026

Research bookmark after the baseline, implementation controls and wording
sensitivity experiment. This records the experimental state and open research
questions; it is not a Git commit or tag.

## Original question

Can a computational model predict how easily people understand an icon's
intended meaning?

## What exists

- All 239 paper icons, published meanings and eight numerical measurements,
  joined through source-traceable identifiers. Three published summary means
  still differ from the reconstructed table; provenance records retain this.
- Reproducible CLIP ViT-B/32 baseline: all 239 icons against 231 unique meanings.
- Initial comparisons with human judgments, including familiarity and agreement.
- Three obvious-image controls pass; original reference code agrees with our
  implementation using the same loaded weights. This is a limited diagnostic.
- A fixed three-template sensitivity experiment and a local visual explorer.

## Main evidence at this point

| Template | Similarity vs human closeness (Spearman) | 95% icon-bootstrap interval |
| --- | ---: | --- |
| Original icon prompt | −0.0327 | −0.1647 to 0.0973 |
| Label alone | 0.1045 | −0.0238 to 0.2380 |
| Symbol meaning prompt | −0.1143 | −0.2409 to 0.0094 |

All three intervals include zero. Wording changes many predictions; none of
these analyses establishes a clear positive association with human closeness.
The label-only change relative to baseline has a paired interval above zero,
which is a different claim from a positive association within that variant.

## What remains unresolved

- A useful predictor of human understandability has not been established.
- Semantic closeness is one human measure, not the whole of understandability.
- Initial agreement and familiarity comparisons are exploratory; no causal or
  held-out predictive claims are supported.
- Sensitivity to wording, the legacy corpus and unresolved table-summary
  differences constrain interpretation. Passing controls does not eliminate
  every possible implementation or dataset problem.

## Possible next research step

Review the next research decision together before implementation. A candidate
is a focused ambiguity analysis: define competing-interpretation scores in
advance, then compare them with correct-meaning concept agreement and answer
agreement, keeping those human outcomes distinct. Existing margin comparisons
are preliminary evidence, not a newly completed ambiguity study.

Do not select prompts per icon, change labels to improve observed outcomes, or
treat raw cosine scores as probabilities. The modern Fluent-icon demonstration
remains secondary. No new experiment is authorized by this bookmark alone.

Evidence: `docs/clip-wording.md`, `docs/clip-sanity.md`,
`docs/experiment-notes.md`, `docs/provenance.md` and saved result artifacts.
