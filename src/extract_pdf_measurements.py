"""Build checked measurements from saved OCR observations and reviewed corrections.

Default: python src/extract_pdf_measurements.py (standard library only).
To rerun OCR: add --refresh-ocr; requires macOS Vision/Swift, pdfplumber, Pillow.
No missing values are imputed. Corrections are explicit source transcriptions.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/mcdougall-1999"
SOURCE = ROOT / "data/raw/mcdougall-1999/paper.pdf"
CHECKSUM = "c34c50131f8936b77ff7feab9eaa83c95dc1e7ac4555659dd154a0a202ecebe1"
FIELDS = ["concreteness", "complexity", "familiarity", "meaningfulness",
          "semantic_distance", "complexity_metric", "concept_agreement_pct",
          "name_agreement_pct"]


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def refresh_ocr():
    import pdfplumber

    work = ROOT / "tmp/pdfs/measurements"
    cells = work / "cells"
    cells.mkdir(parents=True, exist_ok=True)
    with pdfplumber.open(SOURCE) as pdf:
        for page_index in range(8, 32):
            page = pdf.pages[page_index]
            table = max(page.images, key=lambda im: im["width"] * im["height"])
            for slot in range(10):
                icon_id = (page_index - 8) * 10 + slot + 1
                if icon_id > 239:
                    break
                row, col = divmod(slot, 2)
                x = table["x0"] + col * table["width"] * .544
                y = table["top"] + row * table["height"] * .204
                box = (x + table["width"] * .38, y - 2,
                       x + table["width"] * .505, y + table["height"] * .17)
                page.crop(box).to_image(resolution=350).save(cells / f"{icon_id:03}.png")
    executable = work / "ocr"
    subprocess.run(["swiftc", str(ROOT / "src/ocr_measurement_cells.swift"),
                    "-o", str(executable)], check=True)
    result = subprocess.run([str(executable), str(cells)], check=True, capture_output=True)
    # Save separately: changing OCR software must not silently replace reviewed evidence.
    refreshed = work / "ocr-refreshed.json"
    refreshed.write_bytes(result.stdout)
    print(f"Fresh OCR saved to {refreshed}; review differences before replacing measurement-ocr.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-ocr", action="store_true")
    args = parser.parse_args()
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != CHECKSUM:
        raise ValueError("PDF differs from the checked source edition")
    if args.refresh_ocr:
        refresh_ocr()
        return
    evidence = json.loads((DATA / "measurement-ocr.json").read_text())
    if set(evidence) != {f"{i:03}.png" for i in range(1, 240)}:
        raise ValueError("OCR evidence must cover exactly IDs 1-239")
    corrections = read_csv(DATA / "measurement-corrections.csv")
    manifest = read_csv(DATA / "manifest.csv")
    if [int(r["icon_id"]) for r in manifest] != list(range(1, 240)):
        raise ValueError("Manifest must contain consecutive IDs 1-239")
    results = []
    for item in manifest:
        icon_id = int(item["icon_id"])
        observations = [r for r in evidence[f"{icon_id:03}.png"]
                        if re.fullmatch(r"\d+(?:[.,]\d+)?", r["text"].strip())]
        values = [r["text"] for r in sorted(observations, key=lambda r: -r["y"])]
        applied = [r for r in corrections if int(r["icon_id"]) == icon_id]
        # Insert missing observations before applying positional replacements.
        for correction in sorted(applied, key=lambda r: (r["action"] != "insert", int(r["field_index"]))):
            index = int(correction["field_index"])
            if correction["action"] == "insert":
                values.insert(index, correction["value"])
            elif correction["action"] == "replace":
                if values[index] != correction["expected_ocr_text"]:
                    raise ValueError(f"OCR evidence changed for icon {icon_id}, field {index}")
                values[index] = correction["value"]
            else:
                raise ValueError("Unknown correction action")
        if len(values) != 8:
            raise ValueError(f"Icon {icon_id} has {len(values)} measurements, expected 8")
        numbers = [float(v.replace(",", ".")) for v in values]
        if any(not 1 <= v <= 5 for v in numbers[:5]):
            raise ValueError(f"Rating outside 1-5 for icon {icon_id}")
        if not numbers[5].is_integer() or numbers[5] < 0:
            raise ValueError(f"Invalid complexity count for icon {icon_id}")
        if any(not 0 <= v <= 100 for v in numbers[6:]):
            raise ValueError(f"Percentage outside 0-100 for icon {icon_id}")
        if numbers[6] > numbers[7]:
            raise ValueError(f"Concept agreement exceeds name agreement for icon {icon_id}")
        notes = []
        if any(abs(v / 2.5 - round(v / 2.5)) > 1e-8 for v in numbers[6:]):
            notes.append("Printed percentage is not a multiple of 2.5; retained as printed")
        result = {key: item[key] for key in ["icon_id", "label", "image", "pdf_page", "printed_page"]}
        result.update({key: str(int(value)) if key == "complexity_metric" else f"{value:.2f}"
                       for key, value in zip(FIELDS, numbers)})
        result.update(source_sha256=CHECKSUM, verification="OCR assisted; visually checked against scan",
                      manual_correction_count=len(applied), source_note="; ".join(notes))
        results.append(result)
    output = DATA / "measurements.csv"
    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    # Table 1 is an independent comparison, not a target to force data to fit.
    published = dict(zip(FIELDS, [3.26, 2.62, 2.97, 2.80, 2.59, 8.60, 15.49, 31.39]))
    checks = {}
    for field in FIELDS:
        column = [float(row[field]) for row in results]
        mean = statistics.mean(column)
        checks[field] = dict(extracted_mean=mean, published_table_1_mean=published[field],
                             matches_at_two_decimals=round(mean, 2) == published[field],
                             minimum=min(column), maximum=max(column))
    report = dict(icon_count=len(results), numerical_value_count=len(results) * 8,
                  manual_correction_count=len(corrections), source_sha256=CHECKSUM,
                  summary_comparison=checks,
                  limitation="Some reconstructed means differ from Table 1; cause unresolved. "
                  "Printed per-icon values are retained without adjustment.")
    (DATA / "measurement-validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Wrote {len(results)} icons, {len(results) * 8} measurements to {output}")
    for row in results:
        if row["source_note"]:
            print(f"Source note, icon {row['icon_id']}: {row['source_note']}")


if __name__ == "__main__":
    main()
