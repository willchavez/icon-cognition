"""Extract the ten visually checked icons on the first appendix page.

Requires pdfplumber (including its rendering dependencies) and Pillow.
Run from the repository root: python src/extract_pdf_sample.py
Crop boxes are PDF points, measured from the page's top-left corner.
This deliberately covers only page 9; later pages need separate verification.
"""

import csv
import hashlib
from pathlib import Path

import pdfplumber
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/mcdougall-1999/paper.pdf"
OUTPUT = ROOT / "data/processed/mcdougall-1999-sample"
LABELS = [
    "Add task", "Added fabric web width", "Adjust contrast",
    "Air cooled condenser", "Air vent - right and left outlets",
    "Airborne troops", "Airbrush", "All operators",
    "American health service", "Apple computer",
]


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    checksum = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    rows = []
    sheet = Image.new("RGB", (1000, 500), "white")
    draw = ImageDraw.Draw(sheet)
    with pdfplumber.open(SOURCE) as pdf:
        page = pdf.pages[8]  # PDF page 9, printed page 495
        for index, label in enumerate(LABELS):
            row, col = divmod(index, 2)
            left = 84 if col == 0 else 328
            top = 154 + row * 126
            box = (left, top, left + 88, top + 78)
            rendered = page.crop(box).to_image(resolution=300).original
            filename = f"icon-{index + 1:03d}.png"
            rendered.save(OUTPUT / filename)
            rows.append(dict(
                icon_id=index + 1, label=label, image=filename,
                pdf_page=9, printed_page=495,
                crop_left=box[0], crop_top=box[1],
                crop_right=box[2], crop_bottom=box[3], dpi=300,
                source_sha256=checksum,
                verification="ID and label visually checked; crop visually reviewed",
            ))
            thumbnail = rendered.copy()
            thumbnail.thumbnail((150, 175))
            cell_x, cell_y = (index % 5) * 200, (index // 5) * 250
            sheet.paste(thumbnail, (cell_x + 25, cell_y + 20))
            draw.text((cell_x + 10, cell_y + 205), f"{index + 1}: {label[:25]}", fill="black")
    with (OUTPUT / "manifest.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    sheet.save(OUTPUT / "contact-sheet.png")
    print(f"Extracted {len(rows)} icons to {OUTPUT}")


if __name__ == "__main__":
    main()
