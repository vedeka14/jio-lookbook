# 👗 Jio Lookbook

An AI-powered wardrobe assistant that builds a private wardrobe database from clothing photos using YOLO object detection and color extraction.

This project is part of an AI internship focused on creating an intelligent wardrobe recommendation system that can eventually integrate with JioCloud and provide outfit recommendations based on travel context.

---

# Features

- Clothing detection using YOLO
- Dominant color extraction using OpenCV (HSV)
- Wardrobe database generation (JSON)
- Dataset merging from multiple Roboflow datasets
- Dataset verification with bounding boxes
- GPU-ready configuration (CUDA support)
- Portable project structure using centralized configuration

---

# Project Structure

```
Jio_Lookbook
│
├── data
│   ├── photos
│   ├── color_crops
│   ├── crops
│   ├── output
│   ├── colors.json
│   └── wardrobe.json
│
├── datasets
│
├── models
│
├── scripts
│   ├── build_wardrobe.py
│   ├── color_detection_lab.py
│   ├── config.py
│   ├── demo.py
│   ├── extract_colors.py
│   ├── merge_datasets.py
│   └── verify_samples.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Technologies Used

- Python
- Ultralytics YOLO
- OpenCV
- PyTorch
- NumPy
- Pillow
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

## 3. Detect clothing and build wardrobe

```bash
python scripts/build_wardrobe.py
```

---

## 4. Detect colors only

```bash
python scripts/extract_colors.py
```

---

## 5. View wardrobe database

```bash
python scripts/demo.py
```

---

# Sample Output

```
========== MY WARDROBE ==========

Image      : shirt_01.jpg
Category   : Tshirt
Color      : Sky Blue
Confidence : 0.989
```

---

# Current Pipeline

```
Input Images
      │
      ▼
YOLO Detection
      │
      ▼
Crop Clothing
      │
      ▼
Color Detection
      │
      ▼
Wardrobe JSON
      │
      ▼
Recommendation Engine (Future)
```

---

# Current Project Status

✅ Dataset merging

✅ Clothing detection

✅ Color extraction

✅ Wardrobe JSON generation

✅ GPU-ready project structure

🚧 Outfit recommendation engine

🚧 Travel context detection

🚧 JioCloud integration

🚧 OCR for travel tickets

---

# Future Work

- Detect travel destination using OCR
- Integrate JioCloud APIs
- Outfit recommendation engine
- Similar clothing search
- Color harmony recommendations
- Weather-aware outfit suggestions
- Fine-tune YOLO on larger fashion datasets

---

# Author

**Vedeka Vaswani**

Artificial Intelligence & Data Science Engineering

GitHub: https://github.com/vedeka14