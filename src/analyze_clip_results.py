"""Exploratory rank correlations and disagreements; no model fitting or tuning.

Requires NumPy, already installed for CLIP. Bootstrap intervals resample icons,
not participants, and do not establish generalization beyond this legacy corpus.
"""

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
HUMAN_FIELDS = ["semantic_distance", "familiarity", "concept_agreement_pct",
                "name_agreement_pct", "meaningfulness", "concreteness", "complexity", "complexity_metric"]
SCORES = ["intended_similarity", "intended_minus_best_alternative"]


def ranks(values):
    """One-based average ranks, with exact ties receiving the same rank."""
    _, inverse, counts = np.unique(values, return_inverse=True, return_counts=True)
    return (np.cumsum(counts) - counts + (counts + 1) / 2)[inverse]


def pearson(x, y):
    x, y = np.asarray(x) - np.mean(x), np.asarray(y) - np.mean(y)
    denominator = np.linalg.norm(x) * np.linalg.norm(y)
    return float(np.dot(x, y) / denominator) if denominator > 1e-12 else None


def spearman(x, y, control=None):
    rx, ry = ranks(x), ranks(y)
    if control is not None:
        design = np.column_stack([np.ones(len(x)), ranks(control)])
        rx = rx - design @ np.linalg.lstsq(design, rx, rcond=None)[0]
        ry = ry - design @ np.linalg.lstsq(design, ry, rcond=None)[0]
    return pearson(rx, ry)


def estimate(x, y, indices, control=None):
    value = spearman(x, y, control)
    samples = [spearman(x[idx], y[idx], control[idx] if control is not None else None) for idx in indices]
    finite = [v for v in samples if v is not None]
    return dict(rho=value, n=len(x), ci95=np.quantile(finite, [.025, .975]).tolist() if finite else None,
                valid_bootstrap_samples=len(finite))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--bootstrap", type=int, default=2000)
    args = parser.parse_args()
    if args.bootstrap < 100:
        parser.error("Use at least 100 bootstrap samples")
    source = args.run / "summary.csv"
    with source.open() as stream:
        rows = list(csv.DictReader(stream))
    metadata = json.loads((args.run / "run.json").read_text())
    if [int(r["icon_id"]) for r in rows] != metadata["icon_ids"]:
        raise ValueError("Run metadata and summary IDs differ")
    numbers = {field: np.array([float(r[field]) for r in rows]) for field in HUMAN_FIELDS + SCORES}
    if any(not np.isfinite(values).all() for values in numbers.values()):
        raise ValueError("Nonfinite data; review before analysis")
    rng = np.random.default_rng(20261024)
    indices = rng.integers(0, len(rows), size=(args.bootstrap, len(rows)))
    correlations = {}
    for score in SCORES:
        correlations[score] = {field: estimate(numbers[score], numbers[field], indices)
                               for field in HUMAN_FIELDS}
    partial = estimate(numbers["intended_similarity"], numbers["semantic_distance"], indices,
                       control=numbers["familiarity"])
    model_percentile = (ranks(numbers["intended_similarity"]) - 1) / (len(rows) - 1)
    human_percentile = (ranks(numbers["semantic_distance"]) - 1) / (len(rows) - 1)
    disagreements = []
    for index in np.argsort(model_percentile - human_percentile, kind="stable"):
        r = rows[index]
        disagreements.append(dict(icon_id=int(r["icon_id"]), label=r["label"],
                                  model_percentile=float(model_percentile[index]),
                                  human_closeness_percentile=float(human_percentile[index]),
                                  model_minus_human_percentile=float(model_percentile[index] - human_percentile[index]),
                                  familiarity=float(r["familiarity"])))
    result = dict(
        n=len(rows), candidate_count=len(metadata["candidates"]),
        intended_top1=sum(int(r["intended_rank"]) == 1 for r in rows),
        median_intended_rank=float(np.median([int(r["intended_rank"]) for r in rows])),
        top_prediction_counts=dict(Counter(r["best_label"] for r in rows).most_common()),
        correlations=correlations, semantic_similarity_partial_controlling_familiarity=partial,
        disagreement_order=disagreements, method="Spearman correlation with average ranks for ties",
        primary_comparison="intended_similarity versus semantic_distance (higher means closer)",
        bootstrap=dict(samples=args.bootstrap, seed=20261024, unit="icon", interval="95% percentile"),
        source_summary_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        analysis_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        limitations=["Exploratory associations, not held-out predictive evaluation",
                     "Secondary comparisons are exploratory; no significance claims",
                     "Bootstrap resamples this icon corpus, not participant-level uncertainty",
                     "Partial rank correlation describes association conditional on familiarity; not causation",
                     "Human summary-statistic discrepancies remain unresolved"],
    )
    (args.run / "analysis.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    primary = correlations["intended_similarity"]["semantic_distance"]
    print(f"n={len(rows)}; primary Spearman rho={primary['rho']:.4f}; 95% interval={primary['ci95']}")
    print(f"Partial rank rho controlling familiarity={partial['rho']:.4f}")


if __name__ == "__main__":
    main()
