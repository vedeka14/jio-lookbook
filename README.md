# 👗 Jio Lookbook

An AI-powered wardrobe assistant that understands a user's travel plans and wardrobe to recommend suitable outfits while preserving privacy.

The project builds a private wardrobe database from clothing photos using **OWL-ViT**, extracts structured travel information from flight tickets using **EasyOCR + Ollama (Qwen)**, and lays the foundation for a privacy-preserving outfit recommendation system.

This project is being developed as part of an AI internship focused on combining computer vision, OCR, and recommendation systems with JioCloud.

---

# Features

- ✈️ Flight ticket OCR using EasyOCR
- 🧠 Structured trip information extraction using Ollama (Qwen)
- 👕 Zero-shot clothing detection using OWL-ViT
- 🎨 Clothing color extraction using OpenCV (HSV)
- 👗 Private wardrobe database generation
- 📦 Dataset merging from multiple Roboflow datasets
- ✅ Dataset verification utilities
- 🚀 GPU-ready project structure
- 🔒 Privacy-first recommendation pipeline
- 🔄 Optional OWL-ViT → YOLO annotation workflow for future training

---

# Project Structure

```text
Jio_Lookbook
│
├── data
│   ├── photos/
│   ├── tickets/
│   ├── crops/
│   ├── color_crops/
│   ├── output/
│   │    ├── ocr.json
│   │    └── owlvit.json
│   ├── colors.json
│   └── wardrobe.json
│
├── datasets/
│
├── models/
│
├── scripts
│   ├── config.py
│   │
│   ├── merge_datasets.py
│   ├── verify_samples.py
│   │
│   ├── ocr_ticket.py
│   ├── owlvit_detect.py
│   ├── crop_detections.py
│   ├── extract_colors_owlvit.py
│   ├── build_wardrobe_owlvit.py
│   │
│   ├── build_wardrobe_yolo.py
│   └── demo.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Technologies Used

- Python
- EasyOCR
- Ollama
- Qwen 3
- OWL-ViT
- Hugging Face Transformers
- Ultralytics YOLO
- OpenCV
- PyTorch
- Pillow
- NumPy
- PyYAML

---

# Installation

Clone the repository

```bash
git clone https://github.com/vedeka14/jio-lookbook.git
cd jio-lookbook
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Project

## 1. Merge datasets

```bash
python scripts/merge_datasets.py
```

---

## 2. Verify merged dataset

```bash
python scripts/verify_samples.py
```

---

## 3. Read travel ticket

```bash
python scripts/ocr_ticket.py
```

Outputs

```text
data/output/ocr.json
```

---

## 4. Detect clothing using OWL-ViT

```bash
python scripts/owlvit_detect.py
```

Outputs

```text
data/output/owlvit.json
```

---

## 5. Crop detected clothing

```bash
python scripts/crop_detections.py
```

Outputs

```text
data/crops/
```

---

## 6. Extract clothing colors

```bash
python scripts/extract_colors_owlvit.py
```

Outputs

```text
data/colors.json
```

---

## 7. Build wardrobe database

```bash
python scripts/build_wardrobe_owlvit.py
```

Outputs

```text
data/wardrobe.json
```

---

# Sample Output

Example `wardrobe.json`

```json
[
    {
        "image": "shirt1.jpg",
        "category": "shirt",
        "color": "Sky Blue",
        "confidence": 0.98
    },
    {
        "image": "jeans1.jpg",
        "category": "jeans",
        "color": "Black",
        "confidence": 0.95
    }
]
```

---

# Current Pipeline

```text
                 Flight Ticket
                       │
                       ▼
                  EasyOCR
                       │
                       ▼
                Ollama (Qwen)
                       │
                       ▼
                  ocr.json


              Wardrobe Photos
                       │
                       ▼
                  OWL-ViT
                       │
                       ▼
                 owlvit.json
                       │
                       ▼
               Crop Detections
                       │
                       ▼
              Color Extraction
                       │
                       ▼
                 colors.json
                       │
                       ▼
              Wardrobe Builder
                       │
                       ▼
                wardrobe.json
                       │
                       ▼
          Recommendation Engine (In Progress)
```

---

# Privacy-Preserving Recommendation Flow

The recommendation system is designed so that user photos never leave the local device.

Only wardrobe metadata such as:

```text
Category
Color
```

is used to query the recommendation engine.

Example:

```text
Need:
Blue Jeans
White Shirt

NOT:
User Photos
```

This aligns with the internship requirement of preserving user privacy while enabling personalized recommendations.

---

# Current Project Status

✅ Dataset merging

✅ Dataset verification

✅ OCR pipeline

✅ Flight ticket information extraction

✅ OWL-ViT clothing detection

✅ Clothing cropping

✅ Clothing color extraction

✅ Private wardrobe database generation

✅ GPU-ready project structure

🚧 Trip context understanding

🚧 Mock AJIO catalog integration

🚧 Recommendation engine

🚧 JioCloud integration

🚧 OWL-ViT → YOLO annotation export

🚧 YOLO retraining from reviewed annotations

---

# Future Work

- Detect trip type (Beach, Business, Wedding, etc.)
- Generate outfit recommendations based on trip context
- Match wardrobe with a mock AJIO catalog
- Export reviewed OWL-ViT detections to YOLO format
- Retrain YOLO on reviewed annotations
- Integrate with JioCloud APIs
- Weather-aware outfit recommendations
- Similar clothing search
- Color harmony recommendations

---

# Author

**Vedeka Vaswani**

B.E. Artificial Intelligence & Data Science

GitHub: https://github.com/vedeka14

---