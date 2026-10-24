"""Score McDougall icons against a fixed vocabulary using pretrained CLIP.

Example: .venv/bin/python src/run_clip_experiment.py
This is a pipeline demonstration, not a validated human-understanding model.
"""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/mcdougall-1999"
MODEL = "ViT-B-32"
PRETRAINED = "openai"
PROMPT = "an icon representing {label}"


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def load_inputs(ids):
    if len(ids) < 2 or len(ids) != len(set(ids)):
        raise ValueError("Select at least two distinct icon IDs")
    manifest_rows = read_csv(DATA / "manifest.csv")
    measurement_rows = read_csv(DATA / "measurements.csv")
    manifest = {int(r["icon_id"]): r for r in manifest_rows}
    measurements = {int(r["icon_id"]): r for r in measurement_rows}
    if len(manifest) != len(manifest_rows) or len(measurements) != len(measurement_rows):
        raise ValueError("Duplicate icon ID in source CSVs")
    rows = []
    for icon_id in ids:
        if icon_id not in manifest or icon_id not in measurements:
            raise ValueError(f"Missing manifest or measurements for icon {icon_id}")
        image_row, human_row = manifest[icon_id], measurements[icon_id]
        for field in ["label", "image", "pdf_page", "printed_page", "source_sha256"]:
            if image_row[field] != human_row[field]:
                raise ValueError(f"Source join mismatch for icon {icon_id}: {field}")
        if not image_row["label"].strip() or not (DATA / image_row["image"]).is_file():
            raise ValueError(f"Missing image or label for icon {icon_id}")
        rows.append(human_row)
    if len({r["label"] for r in rows}) < 2:
        raise ValueError("Selected icons must supply at least two distinct candidate labels")
    return rows


def ranking(scores):
    if not all(math.isfinite(s) and -1.00001 <= s <= 1.00001 for s in scores):
        raise ValueError("Invalid cosine similarity")
    # Exact ties use the earlier entry in the fixed vocabulary.
    return sorted(range(len(scores)), key=lambda i: (-scores[i], i))


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--ids", type=int, nargs="+", default=list(range(1, 11)))
    selection.add_argument("--all", action="store_true", help="Use all 239 icons and all unique published labels")
    parser.add_argument("--batch-size", type=int, default=10, help="Limit encoding memory (default: 10)")
    parser.add_argument("--output", type=Path, default=ROOT / "results/clip-first10")
    parser.add_argument("--check-inputs", action="store_true", help="Validate joins without loading CLIP")
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be positive")
    if args.all:
        args.ids = list(range(1, 240))
        if args.output == ROOT / "results/clip-first10":
            args.output = ROOT / "results/clip-all239"
    rows = load_inputs(args.ids)
    # Deduplicate repeated published function names, preserving selected order.
    candidates = list(dict.fromkeys(r["label"] for r in rows))
    prompts = [PROMPT.format(label=label) for label in candidates]
    if args.check_inputs:
        print(f"Validated {len(rows)} images/labels/measurement joins; {len(candidates)} unique candidates")
        return
    if args.output.exists() and any(args.output.iterdir()):
        raise ValueError(f"Output directory is nonempty: {args.output}. Choose a new --output directory")
    started_at = datetime.now(timezone.utc).isoformat()

    import numpy as np
    import open_clip
    from PIL import Image, ImageDraw
    import torch

    random.seed(0)
    np.random.seed(0)
    torch.manual_seed(0)
    torch.set_num_threads(4)
    torch.use_deterministic_algorithms(True)
    print(f"Loading {MODEL}, pretrained={PRETRAINED}, CPU float32", flush=True)
    model, _, preprocess = open_clip.create_model_and_transforms(
        MODEL, pretrained=PRETRAINED, device="cpu", precision="fp32", force_quick_gelu=True)
    model.eval()
    tokenizer = open_clip.get_tokenizer(MODEL)
    image_batches, text_batches, preview = [], [], []
    with torch.inference_mode():
        for start in range(0, len(rows), args.batch_size):
            images = []
            for row in rows[start:start + args.batch_size]:
                with Image.open(DATA / row["image"]) as image:
                    transformed = preprocess(image.convert("RGB"))
                images.append(transformed)
                if len(preview) < 10:
                    normalize = preprocess.transforms[-1]
                    pixels = transformed * torch.tensor(normalize.std)[:, None, None]
                    pixels = pixels + torch.tensor(normalize.mean)[:, None, None]
                    pixels = (pixels.clamp(0, 1).permute(1, 2, 0).numpy() * 255).round().astype("uint8")
                    preview.append((row, Image.fromarray(pixels)))
            image_batches.append(model.encode_image(torch.stack(images), normalize=True))
            print(f"Encoded images {min(start + args.batch_size, len(rows))}/{len(rows)}", flush=True)
        for start in range(0, len(prompts), args.batch_size):
            text_batches.append(model.encode_text(tokenizer(prompts[start:start + args.batch_size]), normalize=True))
        image_features = torch.cat(image_batches)
        text_features = torch.cat(text_batches)
        similarities = (image_features @ text_features.T).cpu().tolist()

    summary, pairs = [], []
    for row, scores in zip(rows, similarities):
        ordered = ranking(scores)
        target = candidates.index(row["label"])
        alternative = next(i for i in ordered if i != target)
        result = dict(row)
        result.update(intended_similarity=scores[target], intended_rank=ordered.index(target) + 1,
                      best_label=candidates[ordered[0]], best_similarity=scores[ordered[0]],
                      best_alternative_label=candidates[alternative],
                      best_alternative_similarity=scores[alternative],
                      intended_minus_best_alternative=scores[target] - scores[alternative],
                      candidate_count=len(candidates))
        for rank, index in enumerate(ordered[:3], 1):
            result[f"top_{rank}_label"] = candidates[index]
            result[f"top_{rank}_similarity"] = scores[index]
        summary.append(result)
        for rank, index in enumerate(ordered, 1):
            pairs.append(dict(icon_id=row["icon_id"], intended_label=row["label"],
                              candidate_index=index, candidate_label=candidates[index],
                              prompt=prompts[index], cosine_similarity=scores[index], rank=rank,
                              is_intended=index == target))

    # Fingerprint the actual loaded tensors, not just a mutable checkpoint alias.
    weights = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        array = tensor.detach().cpu().contiguous().numpy()
        weights.update(name.encode())
        weights.update(str(array.dtype).encode())
        weights.update(str(array.shape).encode())
        weights.update(array.tobytes())
    packages = dict(sorted((dist.metadata["Name"], dist.version)
                           for dist in importlib.metadata.distributions() if dist.metadata["Name"]))
    metadata = dict(
        started_at_utc=started_at, completed_at_utc=datetime.now(timezone.utc).isoformat(),
        model=MODEL, pretrained=PRETRAINED,
        activation="QuickGELU (force_quick_gelu=True, matches pretrained checkpoint)",
        weights_state_sha256=weights.hexdigest(), device="cpu", precision="float32", seed=0,
        deterministic_algorithms=True, torch_threads=4, model_eval=True,
        icon_ids=args.ids, candidates=candidates, prompts=prompts, prompt_template=PROMPT,
        batch_size=args.batch_size,
        tie_rule="earlier candidate in recorded vocabulary wins exact cosine ties",
        score="dot product of L2-normalized image/text embeddings; no softmax or logit scaling",
        preprocessing=repr(preprocess), python=sys.version, platform=platform.platform(),
        packages=packages,
        source_files_sha256={str(p.relative_to(ROOT)): file_hash(p) for p in
                             [DATA / "manifest.csv", DATA / "measurements.csv", Path(__file__)]},
        images_sha256={r["image"]: file_hash(DATA / r["image"]) for r in rows},
        source_pdf_sha256=rows[0]["source_sha256"],
        limitations=["Published legacy corpus; not representative of all modern interface icons" if args.all
                     else "Alphabetically selected pipeline sample; not representative",
                     "Ranks depend on this candidate vocabulary and prompt",
                     "Cosine similarity is not a probability of human understanding",
                     "Source measurement summary discrepancies remain unresolved"],
    )
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "summary.csv", summary)
    write_csv(args.output / "similarities.csv", pairs)
    sheet = Image.new("RGB", (1120, 500), "white")
    draw = ImageDraw.Draw(sheet)
    for i, (row, image) in enumerate(preview):
        x, y = i % 5 * 224, i // 5 * 250
        sheet.paste(image, (x, y))
        draw.text((x + 5, y + 230), f"Icon {row['icon_id']}: {row['label'][:25]}", fill="black")
    sheet.save(args.output / "input-preview.png")
    (args.output / "run.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Wrote {len(summary)} summaries and {len(pairs)} pair scores to {args.output}")
    print(f"Intended label ranked first: {sum(r['intended_rank'] == 1 for r in summary)}/{len(summary)}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError) as error:
        sys.exit(str(error))
