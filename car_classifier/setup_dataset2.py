"""
Stanford Car Body Type veri setinden STATION_WAGON, MICRO ve F1 sınıflarını çeker.
"""

import shutil, os
from pathlib import Path
from collections import defaultdict
import kagglehub

PROJECT_CLASSES = ["SUV","VAN","STATION_WAGON","MICRO","F1","SEDAN","HATCHBACK","PICKUP"]
IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

CLASS_MAP = {
    "station wagon":    "STATION_WAGON",
    "station_wagon":    "STATION_WAGON",
    "stationwagon":     "STATION_WAGON",
    "wagon":            "STATION_WAGON",
    "estate":           "STATION_WAGON",
    "micro":            "MICRO",
    "microcar":         "MICRO",
    "mini":             "MICRO",
    "minicar":          "MICRO",
    "city car":         "MICRO",
    "kei":              "MICRO",
    "f1":               "F1",
    "formula 1":        "F1",
    "formula1":         "F1",
    "formula one":      "F1",
    "open wheel":       "F1",
    "open-wheel":       "F1",
    "openwheeler":      "F1",
    "racing":           "F1",
    # Bu dataset SUV/sedan da içerebilir — onları da al
    "suv":              "SUV",
    "sedan":            "SEDAN",
    "hatchback":        "HATCHBACK",
    "pickup":           "PICKUP",
    "pick-up":          "PICKUP",
    "van":              "VAN",
}

def find_image_dirs(root: Path):
    dirs = defaultdict(list)
    for dirpath, _, filenames in os.walk(root):
        imgs = [Path(dirpath) / f for f in filenames
                if Path(f).suffix.lower() in IMG_EXTS]
        if imgs:
            dirs[Path(dirpath).name].extend(imgs)
    return dict(dirs)

def copy_images(src_files, dst_dir: Path, class_name: str, existing_count: int):
    dst_dir.mkdir(parents=True, exist_ok=True)
    count = existing_count
    for src in src_files:
        if src.suffix.lower() not in IMG_EXTS:
            continue
        dst = dst_dir / f"{class_name}_{count}{src.suffix.lower()}"
        shutil.copy2(src, dst)
        count += 1
    return count

def main():
    print("="*60)
    print(" Stanford Car Body Type veri seti indiriliyor...")
    print("="*60)

    kaggle_path = Path(kagglehub.dataset_download(
        "mayurmahurkar/stanford-car-body-type-data"
    ))
    print(f"\n[OK] İndirilen konum: {kaggle_path}\n")

    image_dirs = find_image_dirs(kaggle_path)
    print(f"[INFO] Bulunan görüntü klasörleri ({len(image_dirs)} adet):")
    for dname, imgs in sorted(image_dirs.items()):
        print(f"   {dname:<35s}: {len(imgs)} görüntü")

    dataset_root = Path("dataset")
    unmapped = []

    for kaggle_class, img_files in image_dirs.items():
        key = kaggle_class.lower().strip()
        project_class = CLASS_MAP.get(key)
        if project_class is None:
            unmapped.append(kaggle_class)
            continue

        dst_dir = dataset_root / project_class
        existing = len([f for f in dst_dir.glob("*")
                        if f.suffix.lower() in IMG_EXTS]) if dst_dir.exists() else 0
        new_count = copy_images(img_files, dst_dir, project_class, existing)
        added = new_count - existing
        print(f"[OK]  '{kaggle_class}' → {project_class}  ({added} görüntü eklendi)")

    print("\n" + "="*60)
    print(" GÜNCEL VERİ SETİ DURUMU")
    print(f"\n{'Sınıf':<20} {'Toplam Görüntü':>16}")
    print("-"*38)
    for cls in PROJECT_CLASSES:
        dst_dir = dataset_root / cls
        total = len([f for f in dst_dir.glob("*")
                     if f.suffix.lower() in IMG_EXTS]) if dst_dir.exists() else 0
        flag = "  ⚠ YETERSİZ" if total < 50 else ""
        print(f"{cls:<20} {total:>16}{flag}")

    if unmapped:
        print(f"\n[UYARI] Eşleştirilemeyen klasörler: {unmapped}")
    print("="*60)

if __name__ == "__main__":
    main()
