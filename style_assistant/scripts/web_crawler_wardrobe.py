
import os
import shutil
from pathlib import Path
from bing_image_downloader import downloader
import subprocess

PHOTOS_DIR = Path("fashion_ai/wardrobeinference/data/photos")
TEMP_DIR = Path("temp_downloads")

def main():
    print("?? Clearing existing wardrobe...")
    if PHOTOS_DIR.exists():
        shutil.rmtree(PHOTOS_DIR)
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
        
    queries = [
        ("casual summer outfit full body", 25),
        ("formal office wear full body", 25),
        ("traditional indian wedding outfit", 25),
        ("winter street fashion", 25)
    ]
    
    print("?? Downloading 100 images from the internet...")
    for query, limit in queries:
        downloader.download(query, limit=limit,  output_dir=str(TEMP_DIR), adult_filter_off=True, force_replace=False, timeout=60, verbose=False)
        
    print("?? Moving images to wardrobe folder...")
    count = 1
    for root, dirs, files in os.walk(TEMP_DIR):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                src = Path(root) / file
                ext = src.suffix
                dst = PHOTOS_DIR / f"auto_img_{count:03d}{ext}"
                shutil.copy2(src, dst)
                count += 1
                
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
                
    print(f"? Successfully loaded {count - 1} images into the wardrobe!")
    
    print("?? Running YOLO AI to detect clothing and build database...")
    subprocess.run(["python", "-m", "fashion_ai.wardrobeinference.build_wardrobe_yolo"], check=True)
    
    print("?? All done! You now have a massive automated wardrobe. Restart Streamlit and check it out!")

if __name__ == "__main__":
    main()

