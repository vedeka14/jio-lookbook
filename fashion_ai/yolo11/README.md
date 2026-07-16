# YOLO11 Model Training

This directory contains dataset merging, validation, and training utilities for YOLO11.

## Features

- Merge multiple Roboflow format datasets into a single unified dataset using master categories.
- Remap class IDs and handle class name normalization.
- Draw bounding boxes on dataset splits to verify label correctness.
- Train the YOLO11 model.

## Directory Structure

```
yolo11/
├── config.py
├── merge_datasets.py
├── verify_samples.py
├── datasets/
│   ├── Fashion_Datasets/   # Raw datasets from Roboflow
│   └── merged_dataset/     # Output of merge_datasets.py
└── models/
    ├── yolo11n.pt          # Base model
    └── best.pt             # Trained custom model
```

## Running the Pipeline

### 1. Merge Datasets
Merge the source datasets into the master categories:

```bash
python merge_datasets.py
```

### 2. Verify Merged Dataset
Generate sample images with annotated bounding boxes to verify that labels are correct:

```bash
python verify_samples.py
```

The output images will be saved in `datasets/merged_dataset/verify_samples/`.

### 3. Train YOLO11
Train the model using the Ultralytics CLI:

```bash
yolo detect train model=models/yolo11n.pt data=datasets/merged_dataset/data.yaml epochs=50 imgsz=640
```
