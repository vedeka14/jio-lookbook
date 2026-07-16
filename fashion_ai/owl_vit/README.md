# OWL-ViT Clothing Detection

Detects clothing items from user photos using the pre-trained OWL-ViT object detection model.

## Features

- Uses `google/owlv2-base-patch16-ensemble` model from Hugging Face transformers.
- Runs open-vocabulary detection for a set of defined clothing categories (e.g. Kurta, Saree, Jeans, Shirt, etc.).
- Saves detection coordinates and confidence scores to `data/output/owlvit.json`.

## Directory Structure

```
owl_vit/
├── config.py
├── owlvit_detect.py
└── data/
    └── photos/
```

## Running Detection

To run OWL-ViT detection on photos:

```bash
python owlvit_detect.py
```

Outputs will be saved in `data/output/owlvit.json`.
