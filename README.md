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

Repository scaffolding and initial source discovery only. No dataset has been downloaded, icon-to-measurement mapping verified, model run, or dependencies installed.

## Next steps

1. Inspect the source paper and locate icon images, intended meanings, and human measurement tables.
2. Verify identifiers and measurement scales before preparing a subset.
3. Choose and document model dependencies, then implement a small reproducible experiment.

The October 25, 2026 optional check-in should describe actual completed work and remaining limitations. Written milestone reports remain the student's own work.

## Collaboration

Work in small, reviewable increments. Explain dependency and methodological choices before implementing them. The project owner reviews changes and handles all Git commits; do not commit, rewrite history, or push without explicit authorization.
