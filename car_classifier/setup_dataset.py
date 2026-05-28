"""
============================================================
 VERİ SETİ KURULUM SCRIPTI
============================================================
 Kaggle'dan "cars-body-type-cropped" veri setini indirir ve
 projenin 8-sınıflı dataset/ klasörüne kopyalar.

 Çalıştırma:
     python setup_dataset.py

 İlk çalıştırmada Kaggle kimlik doğrulaması istenebilir.
 ~/.kaggle/kaggle.json dosyası gerekebilir.
============================================================
"""

import shutil
import os
from pathlib import Path
from collections import defaultdict

import kagglehub

# ============================================================
# 1) PROJE SINIFLARI
#    Klasör adları train.py ile birebir uyumlu olmalı
# ============================================================
PROJECT_CLASSES = [
    "SUV", "VAN", "STATION_WAGON", "MICRO",
    "F1", "SEDAN", "HATCHBACK", "PICKUP",
]

# ============================================================
# 2) KAGGLE SINIF ADI → PROJE SINIF ADI EŞLEMESİ
#    Kaggle veri setindeki klasör adlarını proje sınıflarına
#    eşliyoruz. İndirdikten sonra gerçek adları görmek için
#    önce --dry-run ile çalıştırabilirsiniz.
# ============================================================
CLASS_MAP = {
    # Kaggle klasör adı (küçük/büyük harf fark etmez) → proje sınıfı
    "suv":           "SUV",
    "van":           "VAN",
    "minivan":       "VAN",
    "station wagon": "STATION_WAGON",
    "station_wagon": "STATION_WAGON",
    "stationwagon":  "STATION_WAGON",
    "micro":         "MICRO",
    "microcar":      "MICRO",
    "mini":          "MICRO",
    "f1":            "F1",
    "formula":       "F1",
    "open wheel":    "F1",
    "openwheeler":   "F1",
    "sedan":         "SEDAN",
    "hatchback":     "HATCHBACK",
    "pickup":        "PICKUP",
    "pick up":       "PICKUP",
    "pick-up":       "PICKUP",
    "truck":         "PICKUP",
}

# Geçerli görüntü uzantıları
IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def find_image_dirs(root: Path) -> dict[str, list[Path]]:
    """Kök dizinden itibaren görüntü içeren klasörleri bulur.
    Klasör adı → görüntü dosyaları listesi döner.
    """
    dirs = defaultdict(list)
    for dirpath, _, filenames in os.walk(root):
        imgs = [Path(dirpath) / f for f in filenames
                if Path(f).suffix.lower() in IMG_EXTS]
        if imgs:
            dirs[Path(dirpath).name].extend(imgs)
    return dict(dirs)


def copy_images(src_files: list[Path], dst_dir: Path,
                class_name: str, existing_count: int) -> int:
    """Görüntüleri hedef klasöre kopyalar, çakışma olmaması için
    sıralı isimler verir (CLASS_0.jpg, CLASS_1.jpg, ...).
    """
    dst_dir.mkdir(parents=True, exist_ok=True)
    count = existing_count
    for src in src_files:
        ext = src.suffix.lower()
        if ext not in IMG_EXTS:
            continue
        dst = dst_dir / f"{class_name}_{count}{ext}"
        shutil.copy2(src, dst)
        count += 1
    return count


def main(dry_run: bool = False):
    print("=" * 60)
    print(" Kaggle veri seti indiriliyor...")
    print("=" * 60)

    # ---- İndir ----
    kaggle_path = kagglehub.dataset_download(
        "ademboukhris/cars-body-type-cropped"
    )
    kaggle_path = Path(kaggle_path)
    print(f"\n[OK] İndirilen konum: {kaggle_path}\n")

    # ---- Klasör yapısını tara ----
    image_dirs = find_image_dirs(kaggle_path)
    print(f"[INFO] Bulunan görüntü klasörleri ({len(image_dirs)} adet):")
    for dname, imgs in sorted(image_dirs.items()):
        print(f"   {dname:<30s}: {len(imgs)} görüntü")

    # ---- Eşlemeyi uygula ----
    dataset_root = Path("dataset")
    stats = defaultdict(int)
    unmapped = []

    for kaggle_class, img_files in image_dirs.items():
        key = kaggle_class.lower().strip()
        project_class = CLASS_MAP.get(key)

        if project_class is None:
            unmapped.append(kaggle_class)
            continue

        dst_dir = dataset_root / project_class
        existing = len(list(dst_dir.glob("*"))) if dst_dir.exists() else 0

        if dry_run:
            print(f"[DRY] '{kaggle_class}' → {project_class}  "
                  f"({len(img_files)} görüntü kopyalanacak)")
        else:
            new_count = copy_images(img_files, dst_dir, project_class, existing)
            added = new_count - existing
            stats[project_class] += added
            print(f"[OK]  '{kaggle_class}' → {project_class}  "
                  f"({added} görüntü eklendi)")

    # ---- Özet ----
    print("\n" + "=" * 60)
    if dry_run:
        print(" DRY RUN tamamlandı. Gerçek kopyalama için:")
        print("     python setup_dataset.py")
    else:
        print(" KOPYALAMA TAMAMLANDI")
        print(f"\n{'Sınıf':<20} {'Toplam Görüntü':>16}")
        print("-" * 38)
        for cls in PROJECT_CLASSES:
            dst_dir = dataset_root / cls
            total = len(list(dst_dir.glob("*"))) if dst_dir.exists() else 0
            flag = "  ⚠ YETERSİZ" if total < 50 else ""
            print(f"{cls:<20} {total:>16}{flag}")

    if unmapped:
        print(f"\n[UYARI] Eşleştirilemeyen Kaggle klasörleri: {unmapped}")
        print("        CLASS_MAP sözlüğüne manuel ekleyebilirsiniz.")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Kopyalamadan sadece eşlemeyi göster")
    args = ap.parse_args()
    main(dry_run=args.dry_run)
