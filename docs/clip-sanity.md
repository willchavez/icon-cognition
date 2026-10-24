# CLIP sanity check · October 24, 2026

The first icon experiment remains the baseline. These separate diagnostics ask
whether basic recognition works and whether our OpenCLIP implementation agrees
with the original OpenAI CLIP implementation when they share weights.

## Controls and results

Three obvious images—a dog photograph, a photograph containing cats, and the
CLIP diagram—were compared with six labels: dog, cat, diagram, soccer ball,
bicycle, football. All three expected labels ranked first with the baseline
template `an icon representing {label}`. They also ranked first with
`a photo of a {label}` and bare labels. These are repeated checks on three
images, not nine independent examples or a general accuracy benchmark.

An additional wording probe uses the existing football icon (102). Its score
was 0.1986 for `an icon representing football` and 0.2597 for
`an icon representing soccer ball`. Both labels are valid. This demonstrates
wording sensitivity in one example; it does not explain all baseline results.
The smaller answer list means these ranks cannot be compared directly with the
231-label icon experiment.

## Reference comparison

Reference: [OpenAI/CLIP](https://github.com/openai/CLIP), pinned commit
`d05afc436d78f1c48dc0dbf8e5980a9d471f35f6`.
The original architecture loaded the exact same float32 model state used by
OpenCLIP. The fingerprint matches the committed full-corpus baseline.
Preprocessing tensors and text tokens matched exactly. The largest cosine
difference across the tested images, labels and templates was 3.8743e-7
(acceptance tolerance 1e-5). The official README diagram-versus-dog/cat example
also ranked the diagram first.

No implementation discrepancy was found in these checks. Sharing weights
isolates implementation differences; this is not independent checkpoint
verification. Passing these checks does not validate CLIP as a predictor of
human understandability.

## Artifacts and reproduction

- `data/raw/clip-sanity/manifest.json`: source URLs, checksums, pinned reference files.
- `results/clip-sanity/run.json`: all scores, comparisons, hashes and limitations.
- `results/clip-sanity/previews/`: display thumbnails, not model inputs.
- `src/run_clip_sanity.py`: downloads missing controls and reference code after
  verifying SHA-256 checksums; uses the existing pinned environment.
- `results/review/index.html`: visual results, **Sanity check** tab.

Raw control downloads and reference source cache are ignored by Git; the
manifest records the PyTorch Hub dog image, Hugging Face documentation cats,
and pinned OpenAI diagram URLs. Display previews are saved with the results.

```bash
.venv/bin/python src/run_clip_sanity.py
python3 src/build_results_view.py
```

The diagnostic script refuses to overwrite an existing `run.json`. To repeat,
preserve the existing result directory elsewhere first. It does not rewrite
the first-10 or full-239 experiments.

Next: define alternate descriptions consistently before computing a new
corpus result, then compare all variants with the original baseline. Keep
the published labels and human measurements intact.
