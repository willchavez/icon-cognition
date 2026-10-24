"""Compare the fixed three-template experiment with paired icon bootstraps."""

import json
from pathlib import Path

import numpy as np

from analyze_clip_results import estimate, spearman
from run_clip_experiment import read_csv, file_hash

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/clip-wording"


def main():
    if (OUT / "comparison.json").exists():
        raise ValueError("Comparison already exists; preserve it before rerunning")
    plan = json.loads((OUT / "plan.json").read_text())
    runs, records = [], []
    for spec in plan["runs"]:
        source = ROOT / "results" / spec["folder"]
        meta = json.loads((source / "run.json").read_text())
        rows = read_csv(source / "summary.csv")
        if meta["prompt_template"] != spec["template"]:
            raise ValueError("Template differs from plan")
        if meta["prompts"] != [spec["template"].format(label=label) for label in meta["candidates"]]:
            raise ValueError("Unexpected prompts")
        if len(rows) != 239 or len(meta["candidates"]) != 231:
            raise ValueError("Unexpected corpus or vocabulary size")
        if [int(r["icon_id"]) for r in rows] != meta["icon_ids"]:
            raise ValueError("Summary IDs and metadata differ")
        if records:
            baseline_meta, baseline_rows = records[0]
            for key in ["weights_state_sha256", "icon_ids", "candidates", "images_sha256",
                        "preprocessing", "device", "precision", "seed", "batch_size",
                        "activation", "packages", "torch_threads", "deterministic_algorithms"]:
                if meta[key] != baseline_meta[key]:
                    raise ValueError(f"Fixed setting differs: {key}")
            for key in ["data/processed/mcdougall-1999/manifest.csv",
                        "data/processed/mcdougall-1999/measurements.csv"]:
                if meta["source_files_sha256"][key] != baseline_meta["source_files_sha256"][key]:
                    raise ValueError(f"Input source differs: {key}")
            # Compare every source field, including labels, IDs and all human measures.
            for current, original in zip(rows, baseline_rows):
                for key in original:
                    if key not in ["intended_similarity", "intended_rank", "best_label", "best_similarity",
                                   "best_alternative_label", "best_alternative_similarity",
                                   "intended_minus_best_alternative", "top_1_label", "top_1_similarity",
                                   "top_2_label", "top_2_similarity", "top_3_label", "top_3_similarity"]:
                        if current[key] != original[key]:
                            raise ValueError(f"Input row differs: {key}")
        records.append((meta, rows))
        runs.append(dict(spec, source_summary_sha256=file_hash(source / "summary.csv"),
                         source_run_sha256=file_hash(source / "run.json"),
                         source_similarities_sha256=file_hash(source / "similarities.csv")))
    n = len(records[0][1])
    human = np.array([float(r["semantic_distance"]) for r in records[0][1]])
    vectors = [np.array([float(r["intended_similarity"]) for r in rows]) for _, rows in records]
    if not all(np.isfinite(v).all() for v in [human, *vectors]):
        raise ValueError("Nonfinite inputs")
    indices = np.random.default_rng(20261024).integers(0, n, size=(2000, n))
    base_boot = np.array([spearman(vectors[0][idx], human[idx]) for idx in indices])
    for i, run in enumerate(runs):
        rows = records[i][1]
        run["primary"] = estimate(vectors[i], human, indices)
        run["top1"] = sum(int(r["intended_rank"]) == 1 for r in rows)
        run["median_rank"] = float(np.median([int(r["intended_rank"]) for r in rows]))
        run["changed_best_label"] = sum(a["best_label"] != b["best_label"] for a, b in zip(rows, records[0][1]))
        run["rank_improved"] = sum(int(a["intended_rank"]) < int(b["intended_rank"]) for a, b in zip(rows, records[0][1]))
        run["rank_worsened"] = sum(int(a["intended_rank"]) > int(b["intended_rank"]) for a, b in zip(rows, records[0][1]))
        delta_boot = np.array([spearman(vectors[i][idx], human[idx]) for idx in indices]) - base_boot
        run["rho_difference_from_baseline"] = dict(
            value=run["primary"]["rho"] - runs[0]["primary"]["rho"],
            ci95=np.quantile(delta_boot, [.025, .975]).tolist())
    icons = []
    for j, original in enumerate(records[0][1]):
        variants = [dict(key=run["key"], score=float(rows[j]["intended_similarity"]),
                         rank=int(rows[j]["intended_rank"]), best_label=rows[j]["best_label"])
                    for run, (_, rows) in zip(runs, records)]
        icons.append(dict(icon_id=int(original["icon_id"]), label=original["label"],
                          human_closeness=float(original["semantic_distance"]), variants=variants,
                          rank_range=max(v["rank"] for v in variants) - min(v["rank"] for v in variants)))
    result = dict(plan=plan, n=n, candidates=231, runs=runs, icons=icons,
                  fixed_inputs_verified=True, plan_sha256=file_hash(OUT / "plan.json"),
                  script_sha256=file_hash(Path(__file__)),
                  bootstrap=dict(samples=2000, seed=20261024, unit="icon", paired=True,
                                 interval="95% percentile; resample the same icon indices in every template"),
                  limitations=["Exploratory sensitivity analysis, not held-out predictive evaluation",
                               "No synonym edits or per-icon template selection",
                               "Cosine levels across prompts are not calibrated probabilities",
                               "Bootstrap describes icon sampling, not participant uncertainty",
                               "Source measurement summary discrepancies remain unresolved"])
    (OUT / "comparison.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    for run in runs:
        print(f"{run['template']}: rho={run['primary']['rho']:.4f}, top1={run['top1']}/{n}, median rank={run['median_rank']}; delta={run['rho_difference_from_baseline']}")


if __name__ == "__main__":
    main()
