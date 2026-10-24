# First CLIP experiment

This experiment tests the research pipeline with icons 1-10. They are the
first ten alphabetically listed icons, not a representative sample. No training
or fine-tuning is performed.

## Setup

The local `.venv` uses Python 3.12. Exact installed package versions are pinned
in `requirements.txt`. PyTorch runs the model; torchvision supplies image
transforms; OpenCLIP loads the pretrained model and tokenizer; Pillow reads PNGs.
The remaining packages are their dependencies. Extraction tools are separate
from this experiment environment.

For a fresh environment, from the repository root with Python 3.12 installed:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

The current local environment is already installed. Validate the inputs without
loading or downloading the model:

```bash
.venv/bin/python src/run_clip_experiment.py --check-inputs
```

Run the experiment:

```bash
.venv/bin/python src/run_clip_experiment.py
```

The first run downloads pretrained weights into the model library's user cache,
outside Git. Results go into `results/clip-first10/`. A nonempty output directory
is refused so previous evidence is preserved. For a subsequent run:

```bash
.venv/bin/python src/run_clip_experiment.py --output results/clip-first10-repeat
```

## Fixed baseline

- Architecture: OpenCLIP `ViT-B-32`, with the original `openai` pretrained weights
  and `force_quick_gelu=True` to match the checkpoint's training activation.
- Inputs: existing PDF crops, converted to RGB, then the checkpoint's evaluation
  preprocessing. No additional background removal, enhancement, or icon redraws.
- Text: one fixed prompt, `an icon representing {label}`, for every published
  function label. This is a baseline prompting choice, not a tuned result.
- Candidate vocabulary: the ten labels belonging to icons 1-10, in ID order.
  All ten images are compared with the same vocabulary.
- Score: cosine similarity, calculated as the dot product of L2-normalized
  image and text embeddings. No softmax or logit scaling is applied.
- Execution: CPU, float32, evaluation mode, inference without gradients,
  fixed random seeds, deterministic PyTorch algorithms, four CPU threads.
- Ties: earlier candidate in the recorded vocabulary wins an exact score tie.

The script accepts another explicit selection, for example `--ids 1 2 3 4`.
This also changes the candidate vocabulary. Repeated function labels are
deduplicated in first-occurrence order; icon IDs remain distinct. Record the
selection and vocabulary when comparing runs. Encoding uses recorded batches to bound memory; the default batch size is ten.

## Outputs

| File | Contents |
| --- | --- |
| `summary.csv` | One row per icon, including human measurements, intended-label score/rank, top three candidates, strongest alternative, and score margin |
| `similarities.csv` | All image/candidate pairs (100 for the default run), prompts, cosine scores, and ranks |
| `run.json` | Exact candidate vocabulary/prompts, checkpoint tensor fingerprint, input/script hashes, preprocessing, package versions, hardware/software context, seeds, and timestamps |
| `verification.json` | Output validation and comparison with a second local CPU run |

`intended_minus_best_alternative` is the intended-label score minus the highest
score among other candidate labels. A negative margin means an alternative
ranked above the intended label. This depends on the vocabulary and is not a
calibrated measure of human ambiguity. The human measurements are copied from
the checked source table by icon ID, with source notes preserved.

## Interpretation limits

Cosine similarity is not a probability of human understanding. Ranking first
among ten labels does not show that a person would spontaneously name the icon
correctly. A small alphabetic sample, limited vocabulary, scan quality, text
wording, learned model associations, and possible training-data overlap limit
interpretation. Bitwise reproducibility is checked on the local environment;
different hardware or library versions may differ numerically.

The source's `semantic_distance` score increases with closeness: larger model
similarity would be expected to correlate positively with it if the hypothesis
holds. Name agreement can reflect agreement on an incorrect meaning; it must
not be treated as intended-meaning accuracy. See
`measurement-dictionary.md` for definitions and the unresolved summary-statistic
discrepancies. This first experiment does not compute inferential correlations
or establish predictive validity.

## Implementation references

- [OpenCLIP usage and pretrained-model documentation](https://github.com/mlfoundations/open_clip)
- [OpenCLIP model implementation](https://github.com/mlfoundations/open_clip/blob/main/src/open_clip/model.py)

Observed results and verification are recorded in `experiment-notes.md`.

## Expanded corpus and analysis

The first ten-icon baseline remains unchanged. To run all 239 icons against
all 231 unique published function labels:

```bash
.venv/bin/python src/run_clip_experiment.py --all
```

Image and text encoding now use batches of ten to bound memory. This batching
change reproduced the original ten-icon score CSVs byte for byte. Model,
checkpoint, activation, RGB conversion, evaluation transforms, and prompt remain
fixed. The optional `--batch-size` is recorded in run metadata. `--all` and
`--ids` are mutually exclusive. The selected images after preprocessing are
saved in `input-preview.png` (first ten in the selection). The original default
output directory remains protected from overwrites.

Compute exploratory correlations and rebuild the visual results explorer:

```bash
.venv/bin/python src/analyze_clip_results.py results/clip-first10
.venv/bin/python src/analyze_clip_results.py results/clip-all239
python3 src/build_results_view.py
```

The analysis script uses NumPy, already a CLIP dependency. Spearman coefficients
use average ranks for ties. Primary comparison: intended-label cosine similarity
versus human semantic closeness. Secondary associations include familiarity,
concept/name agreement, and the intended-label margin. These are exploratory,
not additional confirmed hypotheses. Partial rank correlation regresses each
variable's ranks on an intercept and familiarity ranks, then correlates the
residuals; it describes a conditional association rather than a causal effect.

Each 95% percentile interval uses 2,000 paired bootstrap resamples of icons,
with seed 20261024. These intervals describe icon-resampling variability in
this corpus, not participant-level uncertainty or guaranteed generalization.
Related icons and repeated labels may reduce effective independence. No
significance testing, model fitting, or prompt selection was performed.

The disagreement ordering compares each icon's model-similarity percentile
with its human-closeness percentile. The most negative differences identify
examples of high human closeness with relatively low model scores. This is
an inspection aid, not an error probability or learned predictor.

`analysis.json` contains all coefficients, intervals, example ordering, source
hashes, and method settings. A different number of candidate meanings changes
retrieval ranks, so the 2/10 and 25/239 rank-first counts are not directly
comparable measures of progress.

## Visual results explorer

`results/review/index.html` contains the saved results and all icon images.
It needs no JavaScript packages, external image requests, or data service.
The source template is `src/results-view.html`; regenerate it with the command
above after updating the analyzed results. The explorer supports selecting a
run, choosing a human comparison, clicking scatterplot points, searching and
filtering icon cards, and inspecting the corrected source values in Data audit.

For the Codex in-app browser, start the local preview from the repository root:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory results/review
```

Then open http://127.0.0.1:8765/. The server only exposes the generated report
folder and listens on loopback. Stop that terminal process with Ctrl-C when
finished. The report can be regenerated entirely from the saved data without
rerunning the model.
