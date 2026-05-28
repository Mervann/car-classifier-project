"""
F1 ve MICRO sınıflarını doldurmak için ek dataset'ler indirir.
"""

import shutil, os
from pathlib import Path
from collections import defaultdict
import kagglehub

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

def find_all_images(root: Path) -> list[Path]:
    imgs = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if Path(f).suffix.lower() in IMG_EXTS:
                imgs.append(Path(dirpath) / f)
    return imgs

def find_image_dirs(root: Path) -> dict:
    dirs = defaultdict(list)
    for dirpath, _, filenames in os.walk(root):
        imgs = [Path(dirpath) / f for f in filenames
                if Path(f).suffix.lower() in IMG_EXTS]
        if imgs:
            dirs[Path(dirpath).name].extend(imgs)
    return dict(dirs)

def copy_images(src_files, dst_dir: Path, class_name: str):
    dst_dir.mkdir(parents=True, exist_ok=True)
    existing = len([f for f in dst_dir.glob("*") if f.suffix.lower() in IMG_EXTS])
    count = existing
    for src in src_files:
        if src.suffix.lower() not in IMG_EXTS:
            continue
        dst = dst_dir / f"{class_name}_{count}{src.suffix.lower()}"
        shutil.copy2(src, dst)
        count += 1
    return count - existing

def main():
    dataset_root = Path("dataset")

    # ============================================================
    # 1) F1 Dataset - loveymishra/f1-image-classification-updated
    # ============================================================
    print("="*60)
    print(" F1 dataset indiriliyor...")
    print("="*60)
    try:
        f1_path = Path(kagglehub.dataset_download(
            "loveymishra/f1-image-classification-updated"
        ))
        print(f"[OK] İndirilen konum: {f1_path}")

        image_dirs = find_image_dirs(f1_path)
        print(f"[INFO] Klasörler ({len(image_dirs)} adet):")
        for d, imgs in sorted(image_dirs.items()):
            print(f"   {d:<35s}: {len(imgs)} görüntü")

        # Tüm görüntüleri F1 klasörüne kopyala
        all_f1_imgs = find_all_images(f1_path)
        added = copy_images(all_f1_imgs, dataset_root / "F1", "F1")
        print(f"[OK] F1 klasörüne {added} görüntü eklendi.")
    except Exception as e:
        print(f"[HATA] F1 dataset indirilemedi: {e}")
        # İkinci F1 kaynağını dene
        try:
            print(" -> vesuvius13/formula-one-cars deneniyor...")
            f1_path = Path(kagglehub.dataset_download(
                "vesuvius13/formula-one-cars"
            ))
            all_f1_imgs = find_all_images(f1_path)
            added = copy_images(all_f1_imgs, dataset_root / "F1", "F1")
            print(f"[OK] F1 klasörüne {added} görüntü eklendi.")
        except Exception as e2:
            print(f"[HATA] İkinci F1 kaynağı da başarısız: {e2}")

    # ============================================================
    # 2) Vehicle Type Dataset - MICRO için
    # ============================================================
    print("\n" + "="*60)
    print(" Vehicle Type dataset indiriliyor (MICRO için)...")
    print("="*60)

    MICRO_KEYWORDS = {
        "micro", "minicar", "mini car", "city car", "citycar",
        "kei", "microcar", "small car", "compact", "mini",
        "smart", "fiat 500", "nano", "tata nano",
    }

    try:
        vt_path = Path(kagglehub.dataset_download(
            "sujaykapadnis/vehicle-type-image-dataset"
        ))
        print(f"[OK] İndirilen konum: {vt_path}")

        image_dirs = find_image_dirs(vt_path)
        print(f"[INFO] Klasörler ({len(image_dirs)} adet):")
        for d, imgs in sorted(image_dirs.items()):
            flag = " <-- MICRO adayı" if any(k in d.lower() for k in MICRO_KEYWORDS) else ""
            print(f"   {d:<35s}: {len(imgs)} görüntü{flag}")

        micro_added = 0
        for dname, imgs in image_dirs.items():
            if any(k in dname.lower() for k in MICRO_KEYWORDS):
                micro_added += copy_images(imgs, dataset_root / "MICRO", "MICRO")
                print(f"[OK]  '{dname}' → MICRO ({len(imgs)} görüntü)")

        if micro_added == 0:
            print("[UYARI] MICRO eşleşmesi bulunamadı.")
    except Exception as e:
        print(f"[HATA] Vehicle Type dataset indirilemedi: {e}")

    # ============================================================
    # 3) Sonuç özeti
    # ============================================================
    PROJECT_CLASSES = ["SUV","VAN","STATION_WAGON","MICRO","F1",
                       "SEDAN","HATCHBACK","PICKUP"]
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
    print("="*60)

if __name__ == "__main__":
    main()
