"""
MICRO sınıfı için web'den araba görüntüsü indirir.
Her arama terimi ayrı klasöre yazılır, sonra hepsi MICRO'ya taşınır.
"""

import shutil
from pathlib import Path
from icrawler.builtin import BingImageCrawler

DST = Path("dataset/MICRO")
DST.mkdir(parents=True, exist_ok=True)

SEARCHES = [
    ("Smart ForTwo car side view",  25),
    ("Tata Nano car exterior",      25),
    ("Kia Picanto car",             25),
    ("Suzuki Alto hatchback car",   25),
    ("Renault Twingo car",          20),
    ("Fiat 500 minicar",            20),
    ("Hyundai i10 small car",       20),
    ("microcar city car",           20),
]

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

def count_images(folder: Path) -> int:
    return len([f for f in folder.glob("*") if f.suffix.lower() in IMG_EXTS])

existing = count_images(DST)
counter = existing

for keyword, max_num in SEARCHES:
    tmp = Path(f"_tmp_{keyword[:15].replace(' ','_')}")
    tmp.mkdir(exist_ok=True)

    print(f"\n>>> '{keyword}' ({max_num} görüntü hedef)")
    try:
        crawler = BingImageCrawler(
            storage={"root_dir": str(tmp)},
            downloader_threads=4,
            parser_threads=2,
            log_level=40,          # sadece ERROR logları göster
        )
        crawler.crawl(keyword=keyword, max_num=max_num, min_size=(80, 80))
    except Exception as e:
        print(f"  [UYARI] {e}")

    # Bu aramanın indirdiklerini DST'ye taşı
    moved = 0
    for f in tmp.glob("*"):
        if f.suffix.lower() in IMG_EXTS:
            shutil.move(str(f), DST / f"MICRO_{counter}{f.suffix.lower()}")
            counter += 1
            moved += 1
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"    {moved} görüntü eklendi  (toplam: {counter})")

print(f"\n{'='*50}")
print(f"MICRO toplam görüntü: {count_images(DST)}")
print("="*50)
