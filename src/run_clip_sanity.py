"""Small diagnostic controls, plus the official CLIP code with the same weights.

Downloads SHA-256-checked public controls and pinned official reference source
when missing. Does not change or rerun the committed icon experiments.
"""

from datetime import datetime, timezone
import hashlib
import importlib
import json
from pathlib import Path
import sys
from urllib.request import urlretrieve

import open_clip
from PIL import Image
import torch

from run_clip_experiment import MODEL, PRETRAINED, PROMPT, file_hash, ranking

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/clip-sanity"
OUT = ROOT / "results/clip-sanity"
LABELS = ["dog", "cat", "diagram", "soccer ball", "bicycle", "football"]
TEMPLATES = [PROMPT, "a photo of a {label}", "{label}"]


def checked_download(url, path, checksum):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        print(f"Downloading {path.name}", flush=True)
        urlretrieve(url, path)
    if file_hash(path) != checksum:
        raise ValueError(f"Checksum mismatch for {path}; review source before continuing")


def main():
    if (OUT / "run.json").exists():
        raise ValueError("Sanity results already exist; preserve them before rerunning")
    manifest = json.loads((RAW / "manifest.json").read_text())
    for item in manifest["images"]:
        checked_download(item["url"], RAW / item["file"], item["sha256"])
    reference_info = manifest["reference"]
    reference_dir = ROOT / "tmp/clip-reference" / reference_info["commit"]
    for name, checksum in reference_info["files"].items():
        url = f"https://raw.githubusercontent.com/openai/CLIP/{reference_info['commit']}/clip/{name}"
        checked_download(url, reference_dir / "clip" / name, checksum)
    sys.path.insert(0, str(reference_dir))
    reference = importlib.import_module("clip")
    if Path(reference.__file__).resolve().parent != reference_dir / "clip":
        raise ValueError("Unexpected reference package path")
    torch.set_num_threads(4)
    torch.manual_seed(0)
    torch.use_deterministic_algorithms(True)
    model, _, preprocess = open_clip.create_model_and_transforms(
        MODEL, pretrained=PRETRAINED, force_quick_gelu=True, device="cpu", precision="fp32")
    model.eval()
    tokenizer = open_clip.get_tokenizer(MODEL)
    # Explicit original architecture, loading the exact same float32 state.
    ref = reference.model.CLIP(
        embed_dim=512, image_resolution=224, vision_layers=12, vision_width=768,
        vision_patch_size=32, context_length=77, vocab_size=49408,
        transformer_width=512, transformer_heads=8, transformer_layers=12)
    ref.load_state_dict(model.state_dict(), strict=True)
    ref.float().eval()
    controls = [dict(item, path=RAW / item["file"], kind="new control") for item in manifest["images"]]
    controls.append(dict(id="football-icon", path=ROOT / "data/processed/mcdougall-1999/icon-102.png",
                         expected_label="soccer ball", kind="appearance diagnostic; not a new control"))
    images = [Image.open(item["path"]).convert("RGB") for item in controls]
    image_batch = torch.stack([preprocess(image) for image in images])
    reference_batch = torch.stack([reference.clip._transform(224)(image) for image in images])
    preprocessing_delta = float((image_batch - reference_batch).abs().max())
    result_rows, text_deltas, score_deltas = [], [], []
    tokens_match = True
    with torch.inference_mode():
        image_features = model.encode_image(image_batch, normalize=True)
        ref_images = torch.nn.functional.normalize(ref.encode_image(reference_batch), dim=-1)
        image_delta = float((image_features - ref_images).abs().max())
        for template in TEMPLATES:
            prompts = [template.format(label=label) for label in LABELS]
            tokens = tokenizer(prompts)
            tokens_match = tokens_match and torch.equal(tokens, reference.tokenize(prompts))
            text_features = model.encode_text(tokens, normalize=True)
            ref_text = torch.nn.functional.normalize(ref.encode_text(reference.tokenize(prompts)), dim=-1)
            text_deltas.append(float((text_features - ref_text).abs().max()))
            scores = image_features @ text_features.T
            reference_scores = ref_images @ ref_text.T
            score_deltas.append(float((scores - reference_scores).abs().max()))
            for item, values in zip(controls, scores.tolist()):
                order = ranking(values)
                result_rows.append(dict(
                    image_id=item["id"], kind=item["kind"], template=template,
                    expected_label=item["expected_label"], best_label=LABELS[order[0]],
                    expected_rank=order.index(LABELS.index(item["expected_label"])) + 1,
                    rankings=[dict(label=LABELS[i], cosine=values[i], rank=rank)
                              for rank, i in enumerate(order, 1)]))
        # Published README control: diagram versus a dog and a cat.
        official_prompts = ["a diagram", "a dog", "a cat"]
        official_features = model.encode_text(tokenizer(official_prompts), normalize=True)
        official_values = (image_features[2:3] @ official_features.T)[0].tolist()
    weights = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        array = tensor.detach().cpu().contiguous().numpy()
        weights.update(name.encode()); weights.update(str(array.dtype).encode())
        weights.update(str(array.shape).encode()); weights.update(array.tobytes())
    baseline = json.loads((ROOT / "results/clip-all239/run.json").read_text())
    fingerprint_match = weights.hexdigest() == baseline["weights_state_sha256"]
    agreement = (tokens_match and preprocessing_delta == 0 and image_delta < 1e-5
                 and max(text_deltas) < 1e-5 and max(score_deltas) < 1e-5 and fingerprint_match)
    if not agreement:
        raise ValueError("Reference or checkpoint check failed; investigate before interpreting results")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "previews").mkdir(exist_ok=True)
    for item, image in zip(controls, images):
        image.thumbnail((420, 240))
        image.save(OUT / "previews" / f"{item['id']}.png")
    primary = [r for r in result_rows if r["kind"] == "new control" and r["template"] == PROMPT]
    output = dict(
        completed_at_utc=datetime.now(timezone.utc).isoformat(), model=MODEL, pretrained=PRETRAINED,
        activation="QuickGELU", device="cpu", precision="float32", labels=LABELS, templates=TEMPLATES,
        primary_control_count=len(primary), primary_controls_passed=sum(r["expected_rank"] == 1 for r in primary),
        new_control_cases=[i["id"] for i in manifest["images"]], results=result_rows,
        reference=dict(commit=reference_info["commit"], same_loaded_weights=True,
                       tokens_identical=tokens_match, preprocessing_max_abs_delta=preprocessing_delta,
                       image_embedding_max_abs_delta=image_delta, text_embedding_max_abs_delta=max(text_deltas),
                       cosine_max_abs_delta=max(score_deltas), tolerance=1e-5, passed=agreement),
        official_readme_control=dict(prompts=official_prompts, cosines=official_values,
                                     best_label=official_prompts[max(range(3), key=lambda i: official_values[i])]),
        weights_state_sha256=weights.hexdigest(), weights_match_committed_baseline=fingerprint_match,
        source_manifest_sha256=file_hash(RAW / "manifest.json"), script_sha256=file_hash(Path(__file__)),
        images_sha256={item["id"]: file_hash(item["path"]) for item in controls},
        limitations=["Three new obvious controls, not a recognition benchmark",
                     "Football and soccer ball are valid related labels; the alias probe tests wording sensitivity",
                     "Reference comparison isolates implementation differences using the same downloaded weights",
                     "Passing controls does not validate the model as a predictor of human understandability"],
    )
    (OUT / "run.json").write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")
    print(f"Current-prompt controls: {output['primary_controls_passed']}/{len(primary)}")
    print(f"Reference cosine maximum difference: {max(score_deltas):.2e}")
    print(f"Committed checkpoint fingerprint matches: {fingerprint_match}")


if __name__ == "__main__":
    main()
