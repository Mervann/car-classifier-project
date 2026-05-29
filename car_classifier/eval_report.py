"""Val seti üzerinde sklearn classification_report çalıştırır."""
import copy
import torch
import numpy as np
from pathlib import Path
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms
from sklearn.metrics import classification_report, confusion_matrix

from train import build_model, IMAGENET_MEAN, IMAGENET_STD

CKPT_PATH = Path("saved_model/car_body_classifier.pt")
DATA_DIR   = "dataset"
VAL_SPLIT  = 0.15
SEED       = 42
IMG_SIZE   = 224
BATCH      = 32

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
ckpt   = torch.load(CKPT_PATH, map_location=device)
model  = build_model(num_classes=len(ckpt["folder_classes"]), dropout=0.3).to(device)
model.load_state_dict(ckpt["state_dict"])
model.eval()

eval_tf = transforms.Compose([
    transforms.Resize(int(IMG_SIZE * 1.14)),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
])

full_set = datasets.ImageFolder(DATA_DIR, transform=eval_tf)
val_n    = int(len(full_set) * VAL_SPLIT)
train_n  = len(full_set) - val_n
_, val_ds = random_split(full_set, [train_n, val_n],
                         generator=torch.Generator().manual_seed(SEED))

loader = DataLoader(val_ds, batch_size=BATCH, shuffle=False, num_workers=0)

all_preds, all_labels = [], []
with torch.no_grad():
    for imgs, labels in loader:
        preds = model(imgs.to(device)).argmax(1).cpu()
        all_preds.extend(preds.tolist())
        all_labels.extend(labels.tolist())

print(classification_report(all_labels, all_preds,
                             target_names=full_set.classes, digits=4))
cm = confusion_matrix(all_labels, all_preds, normalize="true")
print("\nConfusion Matrix (row=true, col=pred):")
print(np.array2string(cm, precision=3, suppress_small=True))
acc = sum(p == l for p, l in zip(all_preds, all_labels)) / len(all_labels)
print(f"\nVal Accuracy: {acc*100:.2f}%  ({sum(p==l for p,l in zip(all_preds,all_labels))}/{len(all_labels)})")
