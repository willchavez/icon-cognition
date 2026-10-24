"""Build an offline, self-contained HTML explorer from saved experiment results.

Uses only the Python standard library. Regenerate after running analysis.
"""

import base64
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/mcdougall-1999"
NUMBER_FIELDS = ["concreteness", "complexity", "familiarity", "meaningfulness",
                 "semantic_distance", "complexity_metric", "concept_agreement_pct",
                 "name_agreement_pct", "intended_similarity", "best_similarity",
                 "intended_minus_best_alternative"]


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def image_url(path):
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def main():
    runs = {}
    for key, folder, title in [("full", "clip-all239", "Full corpus · 239 icons"),
                               ("sample", "clip-first10", "Initial baseline · 10 icons")]:
        source = ROOT / "results" / folder
        if not (source / "analysis.json").exists():
            continue
        analysis = json.loads((source / "analysis.json").read_text())
        if hashlib.sha256((source / "summary.csv").read_bytes()).hexdigest() != analysis["source_summary_sha256"]:
            raise ValueError(f"Analysis is stale for {folder}")
        rows = read_csv(source / "summary.csv")
        top = {int(r["icon_id"]): [] for r in rows}
        for pair in read_csv(source / "similarities.csv"):
            if int(pair["rank"]) <= 5:
                top[int(pair["icon_id"])].append(dict(label=pair["candidate_label"],
                                                     score=float(pair["cosine_similarity"]), rank=int(pair["rank"])))
        for row in rows:
            row["icon_id"] = int(row["icon_id"])
            row["intended_rank"] = int(row["intended_rank"])
            for field in NUMBER_FIELDS:
                row[field] = float(row[field])
            row["top"] = top[row["icon_id"]]
        runs[key] = dict(title=title, rows=rows, analysis=analysis)
    if not runs:
        raise ValueError("No analyzed runs found")
    image_ids = {r["icon_id"] for run in runs.values() for r in run["rows"]}
    data = dict(runs=runs,
                images={i: image_url(DATA / f"icon-{i:03}.png") for i in sorted(image_ids)},
                validation=json.loads((DATA / "measurement-validation.json").read_text()),
                audit=json.loads((DATA / "measurement-audit.json").read_text()),
                auditImages={i: image_url(DATA / "audit-evidence" / f"icon-{i:03}-complexity-count.png")
                             for i in [34, 136, 172, 201]})
    sanity_path = ROOT / "results/clip-sanity/run.json"
    if sanity_path.exists():
        data["sanity"] = json.loads(sanity_path.read_text())
        data["sanity"]["previews"] = {
            key: image_url(sanity_path.parent / "previews" / f"{key}.png")
            for key in [*data["sanity"]["new_control_cases"], "football-icon"]}
    wording_path = ROOT / "results/clip-wording/comparison.json"
    if wording_path.exists():
        data["wording"] = json.loads(wording_path.read_text())
        for run in data["wording"]["runs"]:
            source = ROOT / "results" / run["folder"]
            for filename, field in [("summary.csv", "source_summary_sha256"),
                                    ("run.json", "source_run_sha256"),
                                    ("similarities.csv", "source_similarities_sha256")]:
                if hashlib.sha256((source / filename).read_bytes()).hexdigest() != run[field]:
                    raise ValueError(f"Wording comparison is stale for {source / filename}")
        if hashlib.sha256(wording_path.with_name("plan.json").read_bytes()).hexdigest() != data["wording"]["plan_sha256"]:
            raise ValueError("Wording comparison plan changed")
    template = (ROOT / "src/results-view.html").read_text()
    if template.count("__RESEARCH_DATA__") != 1:
        raise ValueError("Template must contain exactly one data placeholder")
    embedded = json.dumps(data, separators=(",", ":"), allow_nan=False).replace("<", "\\u003c")
    destination = ROOT / "results/review/index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(template.replace("__RESEARCH_DATA__", embedded))
    print(f"Built {destination} ({destination.stat().st_size:,} bytes); {len(image_ids)} embedded icons")


if __name__ == "__main__":
    main()
