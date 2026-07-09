"""
merge_datasets.py

Merge multiple Roboflow YOLO datasets into one unified dataset.

Features
--------
- Merges train/valid/test splits
- Renames files to avoid collisions
- Remaps class IDs into one master class list
- Normalizes common class name variations
- Skips unknown classes with a warning instead of crashing
- Generates a new data.yaml
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from config import *

ROOT = DATASET_DIR / "Fashion_Datasets"
OUT = DATASET_DIR / "merged_dataset"
TMP = DATASET_DIR / "merged_dataset_tmp"

MASTER_CLASSES = [
    "Churidaar","Dhoti","Hijab","Jeans","Maxi","Pant","Saree","Shorts",
    "Tshirt","Kurta","Shirt","Jacket","Dress","Skirt","Dupatta",
    "Kameez","Shalwar","Design Sherwani","Plain Sherwani",
    "Lehenga","Anarkali","Sharara","Lungi","Handbag","Shoes","Hoodie"
]

NORMALIZE = {
    "shirt":"Shirt","shirts":"Shirt",
    "tshirt":"Tshirt","t-shirt":"Tshirt","tee":"Tshirt","top":"Tshirt",
    "jeans":"Jeans",
    "kurta":"Kurta","kurti":"Kurta","kurtis":"Kurta",
    "saree":"Saree","sari":"Saree","sarees":"Saree",
    "dress":"Dress",
    "jacket":"Jacket","coat":"Jacket",
    "pant":"Pant","pants":"Pant","trouser":"Pant","trousers":"Pant",
    "short":"Shorts","shorts":"Shorts",
    "maxi":"Maxi",
    "dupatta":"Dupatta",
    "kameez":"Kameez",
    "shalwar":"Shalwar","salwar":"Shalwar",
    "design sherwani":"Design Sherwani",
    "desgin sherwani":"Design Sherwani",
    "plain sherwani":"Plain Sherwani",
    "lehenga":"Lehenga",
    "anarkali":"Anarkali",
    "sharara":"Sharara",
    "lungi":"Lungi",
    "dhoti":"Dhoti",
    "hijab":"Hijab",
    "churidaar":"Churidaar",
    "handbag":"Handbag","handbags":"Handbag","bag":"Handbag","bags":"Handbag","purse":"Handbag","backpack":"Handbag",
    "shoe":"Shoes","shoes":"Shoes","sneaker":"Shoes","sneakers":"Shoes",
    "boot":"Shoes","boots":"Shoes","ankle":"Shoes","ankle boot":"Shoes",
    "heel":"Shoes","heels":"Shoes","loafer":"Shoes","loafers":"Shoes",
    "sandal":"Shoes","sandals":"Shoes","slipper":"Shoes","slippers":"Shoes",
    "hoodie":"Hoodie","hoodies":"Hoodie","sweatshirt":"Hoodie"
}

IMAGE_EXTS={".jpg",".jpeg",".png",".bmp",".webp"}
SPLITS=("train","valid","test")

def win(p):
    p=str(p.resolve())
    return "\\\\?\\"+p if os.name=="nt" and not p.startswith("\\\\?\\") else p

def read_yaml(path):
    with open(path,"r",encoding="utf8") as f:
        return yaml.safe_load(f)

def names_list(cfg):
    n=cfg["names"]
    return [n[k] for k in sorted(n,key=lambda x:int(x))] if isinstance(n,dict) else list(n)

def slug(name,i):
    return f"ds{i:02d}_{re.sub(r'[^\\w]+','_',name).strip('_').lower()[:24]}"

def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(win(src),win(dst))

def remove(path):
    if not path.exists():
        return
    if os.name=="nt":
        subprocess.run(["cmd","/c","rmdir","/s","/q",win(path)],check=False)
    shutil.rmtree(path,ignore_errors=True)

def prepare():
    remove(TMP)
    for s in SPLITS:
        (TMP/s/"images").mkdir(parents=True,exist_ok=True)
        (TMP/s/"labels").mkdir(parents=True,exist_ok=True)

def build_id_map(local):
    mapping={}
    for idx,name in enumerate(local):
        canon=NORMALIZE.get(name.strip().lower(),name.strip())
        if canon not in MASTER_CLASSES:
            print(f"[WARNING] Skipping unknown class: {name}")
            continue
        mapping[idx]=MASTER_CLASSES.index(canon)
    return mapping

def remap(src,dst,idmap):
    out=[]
    with open(win(src),"r",encoding="utf8") as f:
        for line in f:
            p=line.strip().split()
            if len(p)<5:
                continue
            cls=int(p[0])
            if cls not in idmap:
                continue
            p[0]=str(idmap[cls])
            out.append(" ".join(p))
    with open(win(dst),"w",encoding="utf8") as f:
        f.write("\n".join(out))

def count(folder):
    return sum(1 for _ in folder.iterdir()) if folder.exists() else 0

def verify(total):
    print("\nVerification")
    disk=0
    for s in SPLITS:
        i=count(TMP/s/"images")
        l=count(TMP/s/"labels")
        disk+=i
        print(f"{s:5} images={i:5} labels={l:5}")
    if disk!=total:
        raise RuntimeError("Image count mismatch.")
    print("Verification passed.")

def main():
    if not ROOT.exists():
        raise FileNotFoundError(ROOT)

    prepare()

    datasets=sorted(
        [d for d in ROOT.iterdir() if d.is_dir() and (d/"data.yaml").exists()],
        key=lambda p:p.name.lower()
    )

    total=0

    for idx,ds in enumerate(datasets,1):
        print(f"Processing {ds.name}")
        idmap=build_id_map(names_list(read_yaml(ds/"data.yaml")))

        ds_slug=slug(ds.name,idx)

        for split in SPLITS:
            imgs=ds/split/"images"
            lbls=ds/split/"labels"

            if not imgs.exists():
                continue

            n=0

            for img in sorted(imgs.iterdir(),key=lambda p:p.name.lower()):
                if img.suffix.lower() not in IMAGE_EXTS:
                    continue

                n+=1
                stem=f"{ds_slug}_{split[0]}_{n:06d}"

                copy(img,TMP/split/"images"/f"{stem}{img.suffix.lower()}")
                total+=1

                lbl=lbls/f"{img.stem}.txt"
                if lbl.exists():
                    remap(lbl,TMP/split/"labels"/f"{stem}.txt",idmap)

    with open(TMP/"data.yaml","w",encoding="utf8") as f:
        yaml.safe_dump({
            "path":str(OUT.resolve()),
            "train":"train/images",
            "val":"valid/images",
            "test":"test/images",
            "nc":len(MASTER_CLASSES),
            "names":{i:n for i,n in enumerate(MASTER_CLASSES)}
        },f,sort_keys=False,allow_unicode=True)

    verify(total)

    remove(OUT)
    TMP.rename(OUT)

    print(f"\nDone! {total} images merged.")
    print(OUT.resolve())

if __name__=="__main__":
    main()
