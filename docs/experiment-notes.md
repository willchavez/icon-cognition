# First CLIP pipeline run - October 24, 2026

## Completed

Ran pretrained CLIP ViT-B/32 on McDougall icons 1-10 against the ten published
function labels, using the fixed prompt `an icon representing {label}`.
The checkpoint's original QuickGELU activation was explicitly selected.
No training or fine-tuning was performed. See `clip-experiment.md` for commands
and methodology, and `results/clip-first10/run.json` for exact configuration.

The isolated environment uses Python 3.12.14, PyTorch 2.14.1, torchvision
0.29.1, OpenCLIP 3.3.0, and Pillow 13.0.0 on this Mac's CPU. All environment
packages are pinned in `requirements.txt`. The existing PDF extraction tools
were not added to this model environment.

## Observed results

- Generated ten per-icon summaries joined to the human measurements and all
  100 image/text candidate scores.
- The intended label ranked first for two icons: 3 (Adjust contrast) and
  9 (American health service). This is retrieval within the ten-label vocabulary,
  not measured human comprehension or a validated prediction rate.
- Added fabric web width ranked first for six images; Air vent - right and
  left outlets ranked first for two. The remaining top predictions were the
  two correct-label cases above.
- Airborne troops (icon 6) ranked its intended label tenth in this vocabulary.

The concentration on a few labels suggests examining candidate wording and
prompt sensitivity in a future experiment. That is a hypothesis for follow-up,
not an established explanation. The baseline prompt was kept fixed for this run.

## Verification

- All ten image/label/measurement joins matched their source records.
- All 100 cosine scores were finite and within [-1, 1]. Each icon had ten
  distinct candidates and ranks 1-10, and its summary matched the pair scores.
- A second run with identical configuration produced byte-identical
  `summary.csv` and `similarities.csv`. Checkpoint and input fingerprints matched;
  timestamps differed as expected. Evidence is in `verification.json`.
- Input checks also exercised repeated published labels, duplicate/missing IDs,
  and deterministic ordering for exact score ties. Dependency consistency passed
  `pip check`.

## Limitations and next decisions

The ten icons form an alphabetical pipeline sample. Candidate count, wording,
prompt, scan quality, and model training associations can affect the results.
No correlations, significance tests, or claims of predictive validity have been
made. The unresolved differences between reconstructed human-measurement means
and the paper's summary means remain documented in `measurement-dictionary.md`.

Next, inspect individual examples and the similarity matrix together before
choosing a broader sample, a candidate vocabulary, or a prompt comparison.
These decisions change what the experiment measures and should be documented
before further interpretation. These notes are an implementation record.

## Expanded baseline - October 24, 2026

The full-corpus run preserves the model and prompt while expanding to 239
images and 231 unique published function labels. It produces 55,209 pair
scores. The input audit reproduced the original ten-icon output CSVs after
adding batching, and the post-preprocessing input preview shows complete
icons without adjacent table text. Source-data auditing corrected four
complexity counts; the expanded run uses the corrected table.

Observed full-corpus results:

- The intended label ranked first for 25 of 239 icons. Median intended-label
  rank was 41 of 231. These retrieval results are not directly comparable
  with the ten-choice baseline, and are not human-comprehension accuracy.
- Primary Spearman correlation between intended-label cosine similarity and
  human semantic closeness: -0.0327; icon-bootstrap 95% interval [-0.1647, 0.0973].
  This fixed baseline shows little overall monotonic association. It does
  not establish that vision-language models cannot predict understandability.
- Similarity versus familiarity: +0.0851; 95% interval [-0.0421, 0.2081].
- The partial rank correlation of similarity and closeness accounting for
  familiarity was -0.0953. This conditional comparison does not establish
  a causal explanation for individual model-human disagreements.
- Similarity versus correct-meaning concept agreement: -0.0256; margin versus
  concept agreement: +0.1105. These secondary analyses are exploratory.
- Bitmap was the top model prediction for 26 icons; Portable files for 17.
  The vocabulary changed, so the initial concentration on Added fabric web
  width did not remain the most frequent prediction in the full run. No
  input/scoring join failure was found that explains the concentration.
- Football (102), Wall (230), Christianity (41), Microphone (146), and Roman
  (187) are the largest high-human-closeness/low-model-similarity percentile
  disagreements under the documented inspection rule. Football has human
  closeness 4.83/5 and concept agreement 75%, but its intended meaning ranks
  221st among 231 model candidates. These are illustrations, not causal findings.

The interactive local explorer presents the scatterplot, individual icons
and ranked alternatives, human measurements, and the source audit. The next
research decision is whether to test a predeclared prompt/vocabulary change
or another model, rather than repeatedly changing prompts to improve these
observed results.

The finalized full-corpus score CSVs were byte-identical on a repeat CPU run
using the same final script, corrected dataset, checkpoint, and image hashes.
All 239 joins, all 55,209 finite scores, and all 231 candidate ranks per icon
passed validation; `verification.json` records the evidence. A geometry check
on all 239 checkpoint-resized/center-cropped inputs found no dark content
touching the image boundary; see `preprocessing-audit.json`. This is an input
check, not proof of accurate recognition.

Browser checks exercised experiment switching, scatterplot selection, the
familiarity axis, icon search and selection, pagination, matching-label
filtering, and the source audit. The explorer presents both runs with their
different candidate counts and notes that their retrieval totals cannot be
compared directly. No external hosting or Git history changes were performed.
