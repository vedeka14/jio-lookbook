# Wardrobe Inference

Builds a private wardrobe database index by using local Vision LLMs (LLaVA) to scan your photos, detect clothing items, and categorize them.

## Features

- **LLaVA Vision Pipeline**:
  - Automatically scans photos in `data/photos/`.
  - Uses a locally hosted LLaVA AI engine (via Ollama) to analyze images.
  - Automatically deduplicates items and filters out AI hallucinations (e.g. "Not Applicable").
  - Includes a built-in 5-minute timeout to gracefully handle GPU locks and CPU-fallback processing.
  - Generates the final private wardrobe index at `data/wardrobe.json`.

## Directory Structure

```
wardrobeinference/
├── build_wardrobe_llava.py  # Main LLaVA inference script
├── extract_colors.py        # Color extraction tools
├── config.py
└── data/
    ├── photos/              # Place user photos here
    └── wardrobe.json        # The generated database (ignored in git)
```

*(Note: Older YOLO and OWL-ViT inference scripts have been deprecated and untracked.)*

## Running the Pipeline

Ensure the Ollama server is running in the background (or use `start_lookbook.bat` from the root). Then run:

```bash
python -m fashion_ai.wardrobeinference.build_wardrobe_llava
```

This script will automatically:
1. Scrub `wardrobe.json` of any past hallucinations on load.
2. Skip photos that are already present in the database.
3. Send new images to the local Ollama AI for categorization.
4. Append newly detected items to `data/wardrobe.json`.
