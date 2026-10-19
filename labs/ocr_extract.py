"""Optional local OCR lab; requires Pillow, pytesseract, and the Tesseract binary.
Run only on an approved synthetic PNG: python examples/labs/ocr_extract.py sample.png
This demo is not a sandbox for arbitrary untrusted documents.
"""
import json
import sys
from pathlib import Path
from PIL import Image
import pytesseract

def extract(path):
    path = Path(path)
    if path.stat().st_size > 5_000_000:
        raise ValueError("file exceeds local lab limit")
    Image.MAX_IMAGE_PIXELS = 10_000_000
    with Image.open(path) as image:
        if image.format != "PNG": raise ValueError("PNG required for this lab")
        if image.width * image.height > 10_000_000: raise ValueError("pixel limit")
        image.load()
        data = pytesseract.image_to_data(image.convert("RGB"),
            output_type=pytesseract.Output.DICT, timeout=10)
    words = []
    for i, text in enumerate(data["text"]):
        if text.strip():
            words.append({"text": text, "page": int(data["page_num"][i]),
                "bbox_pixels": [int(data[k][i]) for k in ("left", "top", "width", "height")],
                "raw_engine_confidence": data["conf"][i]})
    return {"source": path.name, "words": words}

if __name__ == "__main__":
    print(json.dumps(extract(sys.argv[1]), ensure_ascii=False, indent=2))
