"""Extract all 239 icons from the checked two-column appendix layout.

Run from any directory with Python containing pdfplumber and Pillow.
Source coordinates use PDF points from the top-left corner. Published labels
are loaded from the visually checked labels.csv transcription.
"""

import csv
import hashlib
from pathlib import Path

import pdfplumber
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/mcdougall-1999/paper.pdf"
OUTPUT = ROOT / "data/processed/mcdougall-1999"
EXPECTED_SHA256 = "c34c50131f8936b77ff7feab9eaa83c95dc1e7ac4555659dd154a0a202ecebe1"


def main():
    checksum = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if checksum != EXPECTED_SHA256:
        raise ValueError("Source PDF differs from the visually inspected edition")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    previews = OUTPUT / "contact-sheets"
    previews.mkdir(exist_ok=True)
    with (OUTPUT / "labels.csv").open() as stream:
        label_rows = list(csv.DictReader(stream))
    labels = {int(r["icon_id"]): r["label"] for r in label_rows}
    if len(label_rows) != 239 or set(labels) != set(range(1, 240)):
        raise ValueError("Label transcription must contain each ID 1–239 once")
    if any(not label.strip() for label in labels.values()):
        raise ValueError("Label transcription contains a blank label")
    rows = []
    with pdfplumber.open(SOURCE) as pdf:
        for page_index in range(8, 32):
            page = pdf.pages[page_index]
            table = max(page.images, key=lambda im: im["width"] * im["height"])
            sheet = Image.new("RGB", (1000, 500), "white")
            draw = ImageDraw.Draw(sheet)
            for slot in range(10):
                icon_id = (page_index - 8) * 10 + slot + 1
                if icon_id > 239:
                    break
                row, col = divmod(slot, 2)
                left = table["x0"] + col * table["width"] * 0.544
                top = table["top"] + table["height"] * (0.064 + row * 0.204)
                box = (left, top, left + table["width"] * 0.207,
                       top + table["height"] * 0.130)
                # Preserve the previously reviewed first-page sample bounds.
                if page_index == 8:
                    left = 84 if col == 0 else 328
                    top = 154 + row * 126
                    box = (left, top, left + 88, top + 78)
                # Three-line title extends into the standard crop for icon 236.
                if icon_id == 236:
                    box = (box[0], box[1] + 8, box[2], box[3])
                rendered = page.crop(box).to_image(resolution=300).original
                filename = f"icon-{icon_id:03d}.png"
                rendered.save(OUTPUT / filename)
                rows.append(dict(
                    icon_id=icon_id, label=labels[icon_id], image=filename,
                    pdf_page=page_index + 1, printed_page=page_index + 487,
                    crop_left=round(box[0], 4), crop_top=round(box[1], 4),
                    crop_right=round(box[2], 4), crop_bottom=round(box[3], 4),
                    dpi=300, source_sha256=checksum,
                    label_status="visually checked",
                    crop_status="visually reviewed in page contact sheet",
                ))
                thumb = rendered.copy()
                thumb.thumbnail((165, 175))
                x, y = slot % 5 * 200, slot // 5 * 250
                sheet.paste(thumb, (x + 15, y + 15))
                draw.text((x + 10, y + 210), f"Icon {icon_id}", fill="black")
            sheet.save(previews / f"page-{page_index + 1:02d}.png")
    with (OUTPUT / "manifest.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Extracted {len(rows)} icons to {OUTPUT}")


if __name__ == "__main__":
    main()
