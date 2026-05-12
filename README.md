# Image Sharpener

Batch image sharpening tool — Flask backend + browser UI with before/after slider.

## Setup

**1. Create a virtual environment (recommended)**
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**Optional: enable HEIF/AVIF input support**
```bash
pip install -r requirements-heif.txt
```
Use this only if your deployment image includes compatible `libheif` system libraries.

**3. Run**
```bash
python app.py
```

**4. Open in your browser**
```
http://localhost:5000
```

## Usage

1. Drop images (JPG, PNG, WEBP) into the upload zone — or click to browse
2. Pick your **Strength** (1–5) and **Mode**
3. Hit **Sharpen all**
4. Drag the slider on each card to compare before/after
5. Download individual results, or find them all in the `output/` folder

## Modes

| Mode | Best for |
|------|----------|
| Balanced | General purpose |
| Detail boost | Products, textures, macro shots |
| Portrait | Faces, skin tones |
| Landscape | Nature, architecture, travel |

## Output

Enhanced images are saved to `output/sharpened_<original_name>.jpg`
