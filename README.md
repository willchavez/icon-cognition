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

All 239 icons have been extracted from the PDF appendix into `data/processed/mcdougall-1999/`, with a source-coordinate manifest and page contact sheets. All crops and all 239 published labels have been visually reviewed. The checked transcription in `labels.csv` is used to regenerate the manifest. See `docs/provenance.md`. All eight published numerical fields are now transcribed for all 239 icons in `measurements.csv`. See `docs/measurement-dictionary.md` for scale definitions and unresolved differences from three published summary means. No model has been run or project dependencies installed.

## Next steps

1. Review the measurement extraction and the documented summary-statistic discrepancies.
2. Use a traceable small subset to test the experiment pipeline.
3. Choose and document model dependencies, then implement a small reproducible experiment.

The October 25, 2026 optional check-in should describe actual completed work and remaining limitations. Written milestone reports remain the student's own work.

## Collaboration

Work in small, reviewable increments. Explain dependency and methodological choices before implementing them. The project owner reviews changes and handles all Git commits; do not commit, rewrite history, or push without explicit authorization.
