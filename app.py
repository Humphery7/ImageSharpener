import os
import io
import base64
import json
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np

app = Flask(__name__, static_folder="static")
CORS(app)

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def sharpen_image(img: Image.Image, strength: int = 3, mode: str = "balanced") -> Image.Image:
    """
    Apply sharpening and enhancement to a PIL Image.
    strength: 1-5
    mode: balanced | detail | portrait | landscape
    """
    img = img.convert("RGB")

    # --- Unsharp mask sharpening (scales with strength) ---
    radius = 1.5 + (strength - 1) * 0.3
    percent = 80 + (strength - 1) * 40   # 80% at 1, 240% at 5
    threshold = max(1, 4 - strength)
    img = img.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold))

    # --- Mode-specific colour/contrast tweaks ---
    if mode == "detail":
        # Boost contrast and micro-detail
        img = ImageEnhance.Contrast(img).enhance(1.0 + strength * 0.06)
        img = ImageEnhance.Sharpness(img).enhance(1.0 + strength * 0.15)

    elif mode == "portrait":
        # Subtle warmth + gentle brightness lift
        img = ImageEnhance.Color(img).enhance(1.05)
        img = ImageEnhance.Brightness(img).enhance(1.02)
        img = ImageEnhance.Contrast(img).enhance(1.0 + strength * 0.03)

    elif mode == "landscape":
        # Vivid colours, slight contrast
        img = ImageEnhance.Color(img).enhance(1.0 + strength * 0.05)
        img = ImageEnhance.Contrast(img).enhance(1.0 + strength * 0.05)

    else:  # balanced
        img = ImageEnhance.Contrast(img).enhance(1.0 + strength * 0.03)

    return img


def image_to_base64(img: Image.Image, fmt: str = "JPEG") -> str:
    buf = io.BytesIO()
    img.save(buf, format=fmt, quality=95)
    return base64.b64encode(buf.getvalue()).decode()


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/sharpen", methods=["POST"])
def sharpen():
    """
    Accepts multipart/form-data:
      - files[]: one or more image files
      - strength: int 1-5 (default 3)
      - mode: balanced|detail|portrait|landscape (default balanced)
    Returns JSON list of { name, before_b64, after_b64, saved_path }
    """
    strength = int(request.form.get("strength", 3))
    mode = request.form.get("mode", "balanced")
    files = request.files.getlist("files[]")

    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    results = []
    for f in files:
        try:
            img = Image.open(f.stream)
            original_fmt = img.format or "JPEG"
            enhanced = sharpen_image(img.copy(), strength=strength, mode=mode)

            # Save to disk
            safe_name = Path(f.filename).stem
            out_name = f"sharpened_{safe_name}.jpg"
            out_path = OUTPUT_DIR / out_name
            enhanced.save(out_path, format="JPEG", quality=95)

            results.append({
                "name": f.filename,
                "before_b64": image_to_base64(img),
                "after_b64": image_to_base64(enhanced),
                "saved_path": str(out_path),
            })
        except Exception as e:
            results.append({"name": f.filename, "error": str(e)})

    return jsonify(results)


@app.route("/output/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)


if __name__ == "__main__":
    print("\n   Image Sharpener running at http://localhost:5000\n")
    app.run(debug=True, port=5000)
