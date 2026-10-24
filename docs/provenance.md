# Data provenance

## Initial source discovery — October 24, 2026

McDougall, S. J. P., Curry, M. B., & de Bruijn, O. (1999). Measuring symbol and icon characteristics: Norms for concreteness, complexity, meaningfulness, familiarity, and semantic distance for 239 symbols. *Behavior Research Methods, Instruments, & Computers, 31*(3), 487–519.

- DOI: https://doi.org/10.3758/BF03200730
- University repository record: https://eprints.bournemouth.ac.uk/10165/
- Repository PDF: https://eprints.bournemouth.ac.uk/10165/1/Measuring_symbol_and_icon_characteristics_mcdougall__curry_%26_debruijn_1999.pdf
- Bibliographic cross-check: https://pubmed.ncbi.nlm.nih.gov/10502873/

## Verified so far

The bibliographic records identify the paper and report norms for concreteness, complexity, meaningfulness, familiarity, and semantic distance for 239 symbols. A PDF link is available through Bournemouth University's repository.

## Still to verify

- Availability and quality of individual icon images.
- Intended meanings and stable identifiers linking each image to its measurement row.
- Table contents, measurement scales and direction, missing values, and extraction accuracy.
- Whether concept agreement or name agreement measurements are available; do not assume they are included.
- Reuse terms for the paper and individual icons. Public access does not establish permission to redistribute the images.

## PDF extraction sample — October 24, 2026

Downloaded the repository PDF to `data/raw/mcdougall-1999/paper.pdf`.
The appendix is mostly scanned tables, with some additional embedded icon
images; simply exporting PDF image objects does not produce a clean icon set.

Extracted icons 1–10 from PDF page 9 (printed page 495) using fixed rectangular
crops rendered at 300 dpi. The source page and resulting contact sheet were
visually reviewed: all ten icons are complete, without adjacent labels or ratings.
IDs and labels were transcribed from that page. These are published labels;
we have not yet assessed whether each label is suitable as the model's text input.

Outputs are in `data/processed/mcdougall-1999-sample/`. `manifest.csv` records
each ID, label, filename, source page, crop coordinates, rendering resolution,
and source PDF SHA-256. `src/extract_pdf_sample.py` reproduces this sample using
pdfplumber and Pillow; it intentionally does not cover later pages. The bundled
runtime was used, with no dependencies installed into the project.

The scan's pixelation and backgrounds are preserved. Rendering at 300 dpi does
not recover detail absent from the source. Human rating values have not been
transcribed, and no model results have been created. The first page visibly
includes concept agreement and name agreement fields, alongside other ratings.

The repository record permits research, scholarly, or non-commercial access
but does not grant further rights to third-party material. The paper also lists
specific third-party permissions near its end. Image redistribution terms remain
to be checked before publishing extracted assets. The local PDF is ignored by Git.

## Full icon extraction — October 24, 2026

Extracted all 239 published icon IDs from PDF pages 9–32 (printed pages
495–518), with ten icons per page except the final page's nine. Outputs are in
`data/processed/mcdougall-1999/`: 239 PNGs, `manifest.csv`, and 24 page contact
sheets. The original ten-icon sample is preserved separately.

`src/extract_pdf_icons.py` reproduces the full extraction using the bundled
pdfplumber/Pillow runtime. It checks the source PDF SHA-256 before applying
layout-based crops. Each manifest row records its source checksum, page,
crop bounds, rendering resolution, and separate label/crop verification status.
Crop positions track each page's scanned table bounds. Icon 236 has a specific
vertical adjustment to exclude its three-line title.

All 24 appendix pages were inspected in an overview, and all 239 output crops
were visually reviewed in contact sheets for clipping, stray text, and missing
images. The corrected last-page contact sheet was reviewed again. Automated
checks verify IDs 1–239 with no gaps, one readable nonblank PNG per ID, and
no dark content touching the crop borders. These checks support extraction
quality; they do not establish scientific validity of the dataset or labels.

Only the first ten labels are transcribed. Remaining label fields are blank
and marked `not transcribed`; no meanings have been inferred from appearance.
Human measurements remain untranscribed. Images retain source pixelation,
backgrounds, and printed details; no enhancement or semantic redrawing was
applied. The source reuse/redistribution limitations above still apply.

## Complete label transcription — October 24, 2026

All 239 published heading labels are now transcribed in the full manifest,
with `label_status` set to `visually checked`. The earlier statements about
untranscribed labels describe the previous extraction stages.

The transcription was checked against rendered crops of every appendix heading,
including the printed icon IDs. Full pages were inspected for longer headings
whose cropped previews were truncated (including IDs 111, 128, 130, 167, and
179). Printed line breaks were replaced with spaces; spelling, capitalization,
punctuation, and duplicate labels were retained. For example, IDs 62/63 both
say Debug, 197–199 say Search, and 238/239 say Zoom. IDs remain the unique key.
The unusual wording “Protect from heat and radioactive” (179) is as printed,
not a completed or inferred description. These are the headings beside the
icons, not the participant-generated names printed beneath the rating fields.

`data/processed/mcdougall-1999/labels.csv` stores the checked transcription,
source pages, and label verification status independently of generated crops.
`src/extract_pdf_icons.py` now requires that file and validates complete,
nonblank coverage of IDs 1–239 before regenerating the full manifest.
Human ratings remain untranscribed. No model experiment has been run.

## Numerical measurement extraction — October 24, 2026

All eight numerical fields are now extracted for icons 1–239 into
`data/processed/mcdougall-1999/measurements.csv`, keyed by the existing icon
IDs and carrying the published labels, image filenames, source pages, and
PDF SHA-256. Earlier statements that ratings remain untranscribed describe
previous stages. The table holds published aggregate values, not raw responses.

The scanned numeric columns were rendered at 350 dpi with the bundled
pdfplumber/Pillow tools. macOS Vision (via `src/ocr_measurement_cells.swift`)
produced OCR observations, retained as `measurement-ocr.json`. All numeric
columns were visually reviewed against rendered source crops. Fifty-two
manual insertions/replacements, including a value recovered from an expanded
crop for icon 200, are recorded in `measurement-corrections.csv`. No new
project dependencies were installed.

`src/extract_pdf_measurements.py` rebuilds the CSV from the retained OCR and
reviewed corrections with standard-library Python, validating the source hash,
ID coverage, field count, ranges, and joins. Optional fresh OCR is saved
separately for review. Measurements are not merged into the image manifest,
so image regeneration cannot overwrite them.

Procedure pages 490–492 were inspected for definitions and scale direction.
The published semantic-distance rating increases with semantic closeness.
Concept agreement measures identification of the intended meaning, while
name agreement concerns the most common interpretation even if incorrect.
The full definitions and validation limitations are in
`docs/measurement-dictionary.md`.

All five subjective-rating means and all eight observed column ranges match
Table 1 at its printed precision. The other three means do not match; the
cause remains unresolved. Unusual printed percentages for icons 109 and 129
are retained and flagged. Neither agreement values nor component counts were
adjusted to force a match with the summary table. The generated
`measurement-validation.json` records these comparisons. Alternative names
printed beneath the ratings remain untranscribed, and no CLIP results exist.
