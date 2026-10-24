# Predicting Icon Understandability

CS 6795 Cognitive Science project, Fall 2026.

Research question: Can a computational model predict how easily people understand an interface icon's intended meaning?

## Initial scope

Build a small Python research pipeline using a verified subset of approximately 10–20 McDougall icons. Compare pretrained CLIP image–text similarity and ranked candidate meanings with available human measurements. Model similarity is not a probability of human understanding.

## Structure

- `data/raw/`: original source files, subject to source permissions.
- `data/processed/`: verified mappings and prepared inputs.
- `src/`: Python experiment code.
- `results/`: generated experiment outputs.
- `docs/provenance.md`: source records, verification status, and limitations.

## Current status

All 239 icons have been extracted from the PDF appendix into `data/processed/mcdougall-1999/`, with a source-coordinate manifest and page contact sheets. All crops and all 239 published labels have been visually reviewed. The checked transcription in `labels.csv` is used to regenerate the manifest. See `docs/provenance.md`. All eight published numerical fields are now transcribed for all 239 icons in `measurements.csv`. See `docs/measurement-dictionary.md` for scale definitions and unresolved differences from three published summary means. CLIP baselines on icons 1–10 and the complete 239-icon corpus have run successfully, with verified repeat runs. A second measurement audit corrected four complexity counts; three published summary-mean differences remain unresolved. Commands and interpretation limits are in `docs/clip-experiment.md`; actual observations are in `docs/experiment-notes.md`.

## Next steps

1. Review the interactive results and model–human disagreement examples.
2. Discuss the near-zero full-corpus similarity/semantic-closeness association.
3. Choose a documented follow-up experiment before changing the prompt, vocabulary, or model.

The October 25, 2026 optional check-in should describe actual completed work and remaining limitations. Written milestone reports remain the student's own work.

## Collaboration

Work in small, reviewable increments. Explain dependency and methodological choices before implementing them. The project owner reviews changes and handles all Git commits; do not commit, rewrite history, or push without explicit authorization.

## Run the CLIP baseline

The local `.venv` is installed. Validate inputs or run to a new result directory:

```bash
.venv/bin/python src/run_clip_experiment.py --check-inputs
.venv/bin/python src/run_clip_experiment.py --output results/clip-first10-next
```

For setup on another machine, see `docs/clip-experiment.md`. Versions are pinned
in `requirements.txt`. The original completed run is in `results/clip-first10/`.

## Visual results

The generated results explorer is `results/review/index.html`. It includes
clickable scatterplots, all 239 icons, ranked model alternatives, human ratings,
and the measurement audit. For the in-app browser:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory results/review
```

Open http://127.0.0.1:8765/. Stop the preview terminal with Ctrl-C when finished.
The report embeds its images and data and has no external JavaScript dependency.

Rebuild from saved experiment results:

```bash
.venv/bin/python src/analyze_clip_results.py results/clip-all239
python3 src/build_results_view.py
```

The full-corpus baseline compares 239 images against 231 distinct function
labels. Its intended-label similarity has Spearman correlation -0.0327 with
human semantic closeness (95% icon-bootstrap interval -0.1647 to 0.0973).
This baseline provides no clear positive association; it is an exploratory
result, not evidence that all vision-language models fail at this task.
