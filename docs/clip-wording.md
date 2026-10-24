# Wording experiment · October 24, 2026

Question: does changing the words around a published meaning change CLIP's
relationship with human icon–meaning closeness?

The three templates were recorded in `results/clip-wording/plan.json` before
the new corpus runs:

1. `an icon representing {label}` — reuse the preserved full-corpus baseline.
2. `{label}` — new label-only run.
3. `a symbol meaning {label}` — new symbol-prompt run.

All runs use the same 239 icons, 231 distinct published labels in the same
order, human ratings, loaded model weights, preprocessing, CPU float32,
QuickGELU, seed, and batches of 10. The comparison script verifies these
settings, image hashes, environment packages and source data. No synonyms,
label corrections, per-icon template selection, model training, or prompt
ensemble were introduced.

## Results

The primary outcome is Spearman correlation between intended-label cosine
similarity and published semantic distance (whose higher values mean closer).

| Template | Correlation | 95% icon-bootstrap interval | Published label first | Median rank |
| --- | ---: | --- | ---: | ---: |
| Original icon prompt | −0.0327 | −0.1647 to 0.0973 | 25/239 | 41/231 |
| Label only | 0.1045 | −0.0238 to 0.2380 | 27/239 | 43/231 |
| Symbol meaning prompt | −0.1143 | −0.2409 to 0.0094 | 29/239 | 40/231 |

The highest-scoring label changed for 161 icons with label-only wording and
135 icons with symbol wording, relative to baseline. This measures sensitivity,
not improvement. Exact label matches are a separate retrieval task from
correlation with human ratings.

Using 2,000 paired bootstrap samples (seed 20261024), the change in correlation
from baseline was +0.1373 for label-only wording (95% interval 0.0376 to 0.2384)
and −0.0815 for symbol wording (−0.1832 to 0.0153). Each bootstrap sample uses
the same resampled icon indices for both templates. Thus the label-only
comparison shifts upward relative to baseline, while its own association
interval still includes zero. Do not describe these results as proving a
positive human–model relationship or establishing a best prompt.

For icon 102, Football, the intended label ranks 221, 88 and 87 respectively.
Its human closeness remains 4.83/5. This experiment preserves the word Football;
it does not test replacing it with soccer ball. Higher raw cosine under another
template is not a calibrated improvement in understanding.

## Reproduction and review

```bash
.venv/bin/python src/run_clip_experiment.py --all --prompt-template '{label}' --output results/clip-wording/bare
.venv/bin/python src/run_clip_experiment.py --all --prompt-template 'a symbol meaning {label}' --output results/clip-wording/symbol
.venv/bin/python src/analyze_clip_wording.py
python3 src/build_results_view.py
```

Run and comparison outputs refuse to overwrite existing results; preserve them
elsewhere before repeating. New runs save all 55,209 image–text scores, joined
summaries, preprocessing previews and run metadata separately. The comparison
JSON saves coefficients, paired intervals, per-icon changes and source hashes.
The results builder rejects a comparison whose source artifacts or plan changed.

Open the **Wording comparison** tab in the local explorer. It includes the three
summaries, an interval chart, paired changes, and a searchable icon selector with
side-by-side scores and ranks. Neither the original full-corpus experiment nor
the initial 10-icon experiment was rewritten.

## Interpretation and next decision

Wording sensitivity is a finding to report alongside the weak corpus-level
association. All three primary intervals include zero. These are exploratory
results on one legacy corpus, not held-out prediction tests. The bootstrap
resamples icons, not participants; source measurement-summary discrepancies
remain unresolved. The three variants share the same images and are not
independent experiments on new samples.

A synonym study would require a separate, consistently defined description
policy; it is not part of this experiment.
