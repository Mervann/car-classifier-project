"""
============================================================
 MICRO ve STATION_WAGON İÇİN EK VERİ İNDİRME SCRIPTI
============================================================
 Mevcut veri sayıları:
   MICRO         :  73  (hedef: 350+)
   STATION_WAGON : 296  (hedef: 450+)

 Gereksinim:
   pip install icrawler

 Kullanım:
   python download_extra_data.py               # ikisi birden
   python download_extra_data.py --class micro
   python download_extra_data.py --class station_wagon
   python download_extra_data.py --dry-run     # sadece sayıları göster
============================================================
"""

import argparse
import shutil
import time
from pathlib import Path

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

DATASET_ROOT = Path("dataset")


# ============================================================
# Arama Listeleri
# ============================================================

MICRO_SEARCHES = [
    # Gerçek mikro araç modelleri - en ayırt edici görseller
    ("Smart ForTwo car exterior",              30),
    ("Tata Nano microcar",                     30),
    ("Kia Picanto city car",                   30),
    ("Suzuki Alto minicar exterior",           30),
    ("Renault Twingo small car",               30),
    ("Toyota Aygo minicar",                    30),
    ("Volkswagen Up small car",                30),
    ("SEAT Mii city car",                      25),
    ("Mitsubishi i-MiEV microcar",             25),
    ("Daihatsu Mira kei car",                  25),
    ("Fiat Seicento small car",                25),
    ("Bajaj Qute quadricycle",                 20),
    ("Microcar MC2 microcar",                  20),
    ("Aixam microcar",                         20),
    ("microcar exterior side view",            25),
]

STATION_WAGON_SEARCHES = [
    # Estate/Combi/Touring/Variant isimleriyle de bilinen wagon sınıfı
    ("Volvo V60 station wagon",                30),
    ("Audi A4 Avant estate car",               30),
    ("BMW 3 Series Touring wagon",             30),
    ("Subaru Legacy station wagon",            30),
    ("Volkswagen Golf Variant estate",         30),
    ("Skoda Octavia Combi wagon",              30),
    ("Mercedes C-Class Estate wagon",          25),
    ("Ford Focus Estate station wagon",        25),
    ("Peugeot 308 SW estate",                  25),
    ("Renault Megane Estate wagon",            25),
    ("Toyota Corolla Touring wagon",           25),
    ("Volvo V40 estate car",                   25),
    ("Opel Astra Sports Tourer wagon",         20),
    ("station wagon car side view",            30),
    ("estate car exterior",                    25),
]


# ============================================================
# Yardımcı fonksiyonlar
# ============================================================

def count_images(folder: Path) -> int:
    if not folder.exists():
        return 0
    return len([f for f in folder.iterdir() if f.suffix.lower() in IMG_EXTS])


def crawl_and_copy(searches: list, dst_dir: Path, class_name: str,
                   target: int = 400) -> int:
    """icrawler ile görüntü indirir, dst_dir'e kopyalar. Target'a ulaşınca durur."""
    try:
        from icrawler.builtin import BingImageCrawler
    except ImportError:
        print("[HATA] icrawler yüklü değil: pip install icrawler")
        return 0

    dst_dir.mkdir(parents=True, exist_ok=True)
    counter = count_images(dst_dir)
    start_count = counter
    print(f"\n[INFO] {class_name}: mevcut={counter}, hedef={target}")

    for keyword, max_num in searches:
        if counter >= target:
            print(f"  [OK] Hedefe ulaşıldı ({counter}/{target}), durduruluyor.")
            break

        # Hedeften fazla indirme
        remaining = target - counter
        actual_max = min(max_num, remaining + 10)

        tmp_dir = Path(f"_tmp_{class_name}_{keyword[:20].replace(' ', '_')}")
        tmp_dir.mkdir(exist_ok=True)

        print(f"\n  >> '{keyword}' (max {actual_max} görüntü)")
        try:
            crawler = BingImageCrawler(
                storage={"root_dir": str(tmp_dir)},
                downloader_threads=4,
                parser_threads=2,
                log_level=40,
            )
            crawler.crawl(keyword=keyword, max_num=actual_max,
                          min_size=(100, 100), file_idx_offset=0)
        except Exception as e:
            print(f"     [UYARI] {e}")

        moved = 0
        for f in tmp_dir.glob("*"):
            if f.suffix.lower() in IMG_EXTS:
                dst = dst_dir / f"{class_name}_{counter}{f.suffix.lower()}"
                shutil.move(str(f), dst)
                counter += 1
                moved += 1
        shutil.rmtree(tmp_dir, ignore_errors=True)
        print(f"     {moved} görüntü eklendi (toplam: {counter})")
        time.sleep(1)   # sunuculara fazla yük bindirme

    added = counter - start_count
    print(f"\n[SONUÇ] {class_name}: {start_count} → {counter} ({added} eklendi)")
    return added


def print_status():
    """Tüm sınıfların mevcut görüntü sayısını gösterir."""
    classes = ["SUV", "VAN", "STATION_WAGON", "MICRO", "F1",
               "SEDAN", "HATCHBACK", "PICKUP"]
    min_ok = 300

    print("\n" + "="*48)
    print(f"  {'Sınıf':<20} {'Görüntü':>8}  {'Durum'}")
    print("="*48)
    for cls in classes:
        n = count_images(DATASET_ROOT / cls)
        status = "OK" if n >= min_ok else f"EKSİK (hedef: {min_ok}+)"
        print(f"  {cls:<20} {n:>8}  {status}")
    print("="*48)


# ============================================================
# Main
# ============================================================

def main():
    ap = argparse.ArgumentParser(
        description="MICRO ve STATION_WAGON için ek veri indirir."
    )
    ap.add_argument("--class", dest="cls", default="all",
                    choices=["all", "micro", "station_wagon"],
                    help="Hangi sınıf için indirilsin")
    ap.add_argument("--target-micro", type=int, default=380,
                    help="MICRO için hedef görüntü sayısı (varsayılan: 380)")
    ap.add_argument("--target-sw", type=int, default=460,
                    help="STATION_WAGON için hedef görüntü sayısı (varsayılan: 460)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Sadece mevcut sayıları göster, indirme yapma")
    args = ap.parse_args()

    print_status()

    if args.dry_run:
        return

    if args.cls in ("all", "micro"):
        crawl_and_copy(
            MICRO_SEARCHES,
            DATASET_ROOT / "MICRO",
            "MICRO",
            target=args.target_micro,
        )

    if args.cls in ("all", "station_wagon"):
        crawl_and_copy(
            STATION_WAGON_SEARCHES,
            DATASET_ROOT / "STATION_WAGON",
            "STATION_WAGON",
            target=args.target_sw,
        )

    print("\n--- Son durum ---")
    print_status()


if __name__ == "__main__":
    main()
