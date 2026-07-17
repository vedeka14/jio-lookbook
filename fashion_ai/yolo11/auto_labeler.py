import os
import shutil
from pathlib import Path
import yaml
import torch
from PIL import Image
from transformers import OwlViTProcessor, OwlViTForObjectDetection
from tqdm import tqdm

# ==========================================
# Configuration
# ==========================================
RAW_DATASET_DIR = Path(r"C:\Users\Vedeka\Downloads\JioAICloud-Download")
YOLO_DIR = Path(r"C:\Users\Vedeka\Downloads\Jio_Lookbook\fashion_ai\yolo11")
DATA_YAML_PATH = YOLO_DIR / "datasets" / "merged_dataset" / "data.yaml"
OUTPUT_DIR = YOLO_DIR / "datasets" / "auto_labeled_dataset"

LIMIT_PER_CLASS = 50
CONFIDENCE_THRESHOLD = 0.15

# Create output directories
IMG_OUT = OUTPUT_DIR / "images"
LBL_OUT = OUTPUT_DIR / "labels"
IMG_OUT.mkdir(parents=True, exist_ok=True)
LBL_OUT.mkdir(parents=True, exist_ok=True)

print("Loading data.yaml...")
with open(DATA_YAML_PATH, "r") as f:
    data_yaml = yaml.safe_load(f)

# Build a case-insensitive map of class names to IDs
class_map = {name.lower(): id for id, name in data_yaml['names'].items()}
next_class_id = data_yaml['nc']

def get_or_create_class_id(class_name):
    global next_class_id, data_yaml, class_map
    normalized = class_name.replace("_", " ").lower()
    
    if normalized in class_map:
        return class_map[normalized]
    
    # New class!
    new_id = next_class_id
    class_map[normalized] = new_id
    
    # Capitalize for the yaml file (e.g., "kolhapuri chappal" -> "Kolhapuri Chappal")
    pretty_name = normalized.title()
    data_yaml['names'][new_id] = pretty_name
    data_yaml['nc'] += 1
    next_class_id += 1
    
    # Save the updated data.yaml
    with open(DATA_YAML_PATH, "w") as f:
        yaml.dump(data_yaml, f, sort_keys=False)
    
    print(f"Added new class to data.yaml: {pretty_name} (ID: {new_id})")
    return new_id

print("Loading OWL-ViT model...")
processor = OwlViTProcessor.from_pretrained("google/owlvit-base-patch32")
model = OwlViTForObjectDetection.from_pretrained("google/owlvit-base-patch32")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

# Process folders
folders = [f for f in RAW_DATASET_DIR.iterdir() if f.is_dir()]
total_labeled = 0

for folder in folders:
    class_name = folder.name
    class_id = get_or_create_class_id(class_name)
    query = class_name.replace("_", " ")
    
    print(f"\nProcessing class: {query} (ID: {class_id})")
    
    images = list(folder.glob("*.jpg")) + list(folder.glob("*.jpeg")) + list(folder.glob("*.png"))
    images = images[:LIMIT_PER_CLASS]
    
    labeled_for_class = 0
    for img_path in tqdm(images, desc=query):
        try:
            image = Image.open(img_path).convert("RGB")
            inputs = processor(text=[[query]], images=image, return_tensors="pt").to(device)
            
            with torch.no_grad():
                outputs = model(**inputs)
            
            target_sizes = torch.tensor([image.size[::-1]]).to(device)
            results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=CONFIDENCE_THRESHOLD)[0]
            
            if len(results["scores"]) == 0:
                continue # No objects detected above threshold
                
            # Get the highest confidence bounding box
            best_idx = results["scores"].argmax()
            box = results["boxes"][best_idx].tolist() # [xmin, ymin, xmax, ymax]
            score = results["scores"][best_idx].item()
            
            # Convert to YOLO format (normalized center_x, center_y, width, height)
            img_w, img_h = image.size
            xmin, ymin, xmax, ymax = box
            
            x_center = ((xmin + xmax) / 2) / img_w
            y_center = ((ymin + ymax) / 2) / img_h
            width = (xmax - xmin) / img_w
            height = (ymax - ymin) / img_h
            
            # Ensure bounds
            x_center = max(0.0, min(1.0, x_center))
            y_center = max(0.0, min(1.0, y_center))
            width = max(0.0, min(1.0, width))
            height = max(0.0, min(1.0, height))
            
            # Save label and copy image
            out_name = f"{class_name}_{img_path.stem}"
            label_file = LBL_OUT / f"{out_name}.txt"
            
            with open(label_file, "w") as f:
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
                
            shutil.copy(img_path, IMG_OUT / f"{out_name}{img_path.suffix}")
            
            labeled_for_class += 1
            total_labeled += 1
            
        except Exception as e:
            # Skip corrupted images
            pass
            
    print(f"Successfully labeled {labeled_for_class} images for {query}.")

print(f"\nDone! Labeled {total_labeled} images total.")
print(f"Saved to: {OUTPUT_DIR}")
