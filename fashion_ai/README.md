# Fashion AI

Detects clothing items from wardrobe photos.

## Features

- Merge datasets
- Train YOLO
- Detect clothes
- Crop detections
- Extract colors
- Build wardrobe database

## Folder Structure

```
data/
datasets/
models/
scripts/
```

## Run

Merge datasets

```bash
python scripts/merge_datasets.py
```

Train YOLO

```bash
yolo detect train model=models/yolo11n.pt data=datasets/merged_dataset/data.yaml
```

Build wardrobe

```bash
python scripts/build_wardrobe_yolo.py
```

Output

```
wardrobe.json
```