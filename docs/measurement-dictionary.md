# McDougall measurement dictionary

Source: McDougall, Curry, and de Bruijn (1999), DOI
[10.3758/BF03200730](https://doi.org/10.3758/BF03200730).
Procedure and definitions: printed pages 490-492 (PDF pages 4-6).
Per-icon values: appendix, printed pages 495-518 (PDF pages 9-32).

`data/processed/mcdougall-1999/measurements.csv` contains one row per icon,
joined to its image and published function label by `icon_id`. It contains
published aggregate values, not individual participant responses. No values
have been imputed or rescaled.

| Field | Meaning | Scale / direction |
| --- | --- | --- |
| `concreteness` | Mean rating of how much the symbol depicts real objects, materials, or people | 1 = definitely abstract; 5 = definitely concrete |
| `complexity` | Mean rating of visual detail or intricacy | 1 = very simple; 5 = very complex |
| `familiarity` | Mean perceived familiarity, defined through frequency of encounters | 1 = very unfamiliar; 5 = very familiar |
| `meaningfulness` | Mean perceived amount of meaning conveyed | 1 = completely meaningless; larger values indicate more meaning, up to 5 |
| `semantic_distance` | Mean rating of the closeness between the icon and its supplied function | 1 = not closely related; 5 = very strongly related. Higher means **closer**, despite the field name |
| `complexity_metric` | Component count using the Garcia et al. method, measured by an author | Integer count of lines, figures, and letters; not a participant rating or a 1-5 score |
| `concept_agreement_pct` | Participants identifying the intended function/meaning, accepting equivalent wording | Percentage, 0-100; higher means more correct interpretations |
| `name_agreement_pct` | Participants giving the most common interpretation, regardless of correctness | Percentage, 0-100; higher means more agreement, which may be agreement on an incorrect interpretation |

The study reports 200 participants, with separate groups of 40 rating each of
the five subjective dimensions. Meaningfulness raters also supplied meanings;
participants rating an icon completely meaningless were not required to name it.
Semantic-distance raters were given the intended function label. These are
different tasks and should not be treated as interchangeable accuracy measures.

## Other columns

- `icon_id`, `label`, `image`: join key, published function heading, and image
  filename relative to the CSV directory. Repeated labels are preserved.
- `pdf_page`, `printed_page`, `source_sha256`: trace the row to its source.
- `verification`: OCR-assisted values visually checked against the scan.
- `manual_correction_count`: number of recorded insertions/replacements for
  that icon; comma-to-period OCR punctuation normalization is not counted.
- `source_note`: source peculiarities preserved for follow-up.

The occasional alternative interpretation printed below the ratings has not
been transcribed into this table. It is distinct from the intended function
heading in `label`.

## Extraction and regeneration

The extraction used the existing local PDF, pdfplumber/Pillow to render number
columns, and macOS Vision through a small Swift helper for OCR. All 239 number
columns were visually reviewed; 53 explicit corrections are recorded in
`measurement-corrections.csv`. Missing OCR values were read from the scan,
not estimated. Decimal commas recognized by OCR are normalized to periods.
`measurement-ocr.json` preserves OCR observations, confidence, and normalized
bounding boxes relative to each number-column crop; its confidence scores
are not a correctness guarantee.

Rebuild from the reviewed OCR evidence using standard-library Python:

```bash
python3 src/extract_pdf_measurements.py
```

The local PDF must be present at `data/raw/mcdougall-1999/paper.pdf`; its SHA-256
is checked. `--refresh-ocr` rerenders crops at 350 dpi and runs the Swift helper
(requires macOS with Swift/Vision and Python with pdfplumber/Pillow). Fresh
observations go to `tmp/pdfs/measurements/ocr-refreshed.json` for review,
without overwriting reviewed evidence. The crop geometry is explicit in the
Python script; values are read top to bottom in the appendix's eight-field order.

## Validation and unresolved source comparisons

Checks cover 239 consecutive IDs, eight values per icon (1,912 total),
valid rating/percentage/count ranges, source-page joins, and concept agreement
not exceeding name agreement. Each column's observed minimum and maximum
matches the range printed in Table 1.

Two unusual percentages were confirmed visually and retained: icon 109 has
52.00 for both agreement measures; icon 129 has 17.70 for name agreement.
These differ from the 2.5-point increments typical of groups of 40. They are
flagged, not silently changed.

The reconstructed means for the five subjective dimensions agree with Table 1
to its printed two decimal places. Three other reconstructed means differ:

| Measure | Reconstructed mean | Table 1 mean |
| --- | ---: | ---: |
| Complexity metric | 8.5230 | 8.60 |
| Concept agreement (%) | 15.6464 | 15.49 |
| Name agreement (%) | 32.0594 | 31.39 |

The cause is unresolved; extraction mistakes or source inconsistencies remain
possible. The per-icon transcriptions have not been altered to fit summary
statistics. Review these discrepancies before drawing research conclusions.
`measurement-validation.json` records the computed comparison for reruns.

## Second pass over the discrepant columns

A follow-up audit examined all 717 complexity-count, concept-agreement, and
name-agreement values using single-value source crops rather than full number
columns. The second OCR pass agreed numerically on 628 values; all 89 other
results were inspected visually. Most flags were OCR omissions or punctuation
errors. Four actual complexity-count transcription errors were confirmed:

| Icon | Previous transcription | Source value |
| --- | ---: | ---: |
| 34 | 3 | 5 |
| 136 | 8 | 3 |
| 172 | 4 | 6 |
| 201 | 7 | 3 |

These corrections are now applied by `extract_pdf_measurements.py`; the explicit
correction ledger has 53 entries. Source crops are retained in `audit-evidence/`,
and the second OCR observations and audit account are in `measurement-audit-ocr.json`
and `measurement-audit.json`. All 478 agreement values were included in this
second pass; no changes to them were confirmed. None of the five subjective
rating fields changed. This audit did not reconcile the three Table 1 means,
so those differences remain unresolved rather than being attributed definitively
to either the paper or the extraction.
