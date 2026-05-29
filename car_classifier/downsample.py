"""
Her sınıf klasöründen rastgele MAX_PER_CLASS kadar görüntü seçer,
fazlasını dataset_backup/ klasörüne taşır.
"""

import os
import shutil
import random

MAX_PER_CLASS = 600
DATASET_DIR   = "dataset"
BACKUP_DIR    = "dataset_backup"
SEED          = 42
IMG_EXTS      = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

random.seed(SEED)

for cls in sorted(os.listdir(DATASET_DIR)):
    cls_path = os.path.join(DATASET_DIR, cls)
    if not os.path.isdir(cls_path):
        continue

    images = [f for f in os.listdir(cls_path)
              if os.path.splitext(f)[1].lower() in IMG_EXTS]

    if len(images) <= MAX_PER_CLASS:
        print(f"{cls}: {len(images)} görüntü — dokunulmadı")
        continue

    random.shuffle(images)
    to_move = images[MAX_PER_CLASS:]

    backup_cls = os.path.join(BACKUP_DIR, cls)
    os.makedirs(backup_cls, exist_ok=True)

    for fname in to_move:
        shutil.move(os.path.join(cls_path, fname),
                    os.path.join(backup_cls, fname))

    print(f"{cls}: {len(images)} -> {MAX_PER_CLASS} görüntü  ({len(to_move)} yedeklendi)")

print("\nBitti. Yedekler:", BACKUP_DIR)
