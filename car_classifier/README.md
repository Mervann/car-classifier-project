# Araba Gövde Tipi Sınıflandırma — Proje III

**Kocaeli Üniversitesi · Yazılım Laboratuvarı II**

8 sınıflı araba gövde tipi sınıflandırma sistemi.
**Model:** MobileNetV3-Large (transfer learning, ImageNet) • **Framework:** PyTorch • **UI:** Flask

---

## 📁 Sınıflar (proje numaralandırması)

| # | Klasör adı       | Etiket |
|---|------------------|--------|
| 1 | `SUV`            | SUV    |
| 2 | `VAN`            | VAN    |
| 3 | `STATION_WAGON`  | Station Wagon |
| 4 | `MICRO`          | Micro  |
| 5 | `F1`             | Açık Tekerlekli (F1) |
| 6 | `SEDAN`          | Sedan  |
| 7 | `HATCHBACK`      | Hatchback |
| 8 | `PICKUP`         | Pick-Up |

> Etiket numaraları hocaların **Test.txt** scriptinin beklediği numaralandırma ile birebir aynıdır. `predict.py` `preds.txt`'i bu numaralarla üretir.

---

## 🚀 Kurulum

```bash
# 1) Sanal ortam
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate

# 2) Bağımlılıklar
pip install -r requirements.txt
```

GPU'nuz varsa kuruluma uygun CUDA destekli PyTorch sürümünü [pytorch.org](https://pytorch.org/get-started/locally/) sayfasından yükleyin.

---

## 📂 Veri Seti

Görsellerinizi şu yapıda hazırlayın:

```
dataset/
├── SUV/             *.jpg, *.png ...
├── VAN/
├── STATION_WAGON/
├── MICRO/
├── F1/
├── SEDAN/
├── HATCHBACK/
└── PICKUP/
```

**Öneriler**
- Her sınıfta minimum 400-500, ideal 800+ görüntü.
- Sınıflar arası dengesizliği <1:2 oranında tutun.
- Farklı açılar, ışık koşulları, arka planlar → genelleme artar.

**Kaynaklar:**
- Kaggle: [Cars Body Type Cropped](https://www.kaggle.com/datasets/ademboukhris/cars-body-type-cropped)
- Kaggle: [Stanford Car Body Type Data](https://www.kaggle.com/datasets/mayurmahurkar/stanford-car-body-type-data)
- Google Images, Bing, Unsplash, Pexels (manuel toplama)
- F1 sınıfı için: F1 official, Wikimedia Commons

---

## 🎯 Kullanım

### 1) Eğitim

```bash
python train.py
```

Üretilenler:
- `saved_model/car_body_classifier.pt` — eğitilmiş model (~17 MB)
- `saved_model/history.json` — kayıp/doğruluk geçmişi
- `plots/loss_curve.png`, `plots/accuracy_curve.png`

Hiperparametreleri **`train.py` → `CONFIG`** dict'inden ayarlayın.

### 2) Değerlendirme (kendi hold-out setinizde)

Hold-out setinizi şu yapıda hazırlayın (eğitime DAHİL DEĞİL):
```
eval_set/
├── SUV/
├── VAN/
└── ...
```

```bash
python evaluate.py --eval_dir eval_set
```

Üretilenler:
- `plots/confusion_matrix.png` — normalize edilmiş 8x8 heatmap
- `plots/metrics_summary.json` — Accuracy, P, R, F1 (per-class + macro + weighted)
- Terminalde özet metrik tablosu

### 3) Test scripti için preds.txt üretimi

Hocaların paylaşacağı **Test.txt** scriptinin beklediği formatta tahmin dosyası:

```bash
python predict.py --test_dir path/to/test_images --out preds.txt
```

`preds.txt` formatı:
```
image1.jpg | predict:6
image2.jpg | predict:1
```

### 4) Web arayüzü (canlı demo)

```bash
python app.py
```

Tarayıcıdan: **http://127.0.0.1:5000**

Özellikler:
- Drag&drop dosya yükleme
- Görüntü önizlemesi
- Tahmin edilen sınıf + güven skoru
- 8 sınıf için animasyonlu olasılık bar chart'ı
- Anlık çıkarım süresi (ms cinsinden)

---

## ⚙️ Hiperparametreler — Varsayılan

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| Input | 224×224 RGB | MobileNetV3 doğal girişi |
| Batch size | 32 | GPU belleğine göre ayarlanabilir |
| Epochs | 40 (EarlyStopping) | Patience=7 |
| LR backbone | 1e-4 | Pretrained katmanları yavaş güncelle |
| LR head | 1e-3 | Yeni sınıflandırıcı için yüksek LR |
| Optimizer | AdamW | weight_decay=1e-4 |
| Scheduler | Cosine Annealing | Sonlara doğru daha küçük adım |
| Loss | CrossEntropy + label smoothing 0.05 | Aşırı güveni kırar |
| Augmentation | RandomResizedCrop, HFlip, ColorJitter, Rotate(±10°), RandomErasing | Genelleme için |
| Class balancing | WeightedRandomSampler | Dengesizliği telafi eder |

---

## 📊 Beklenen Çıktılar

- **Loss curve** — train/val loss arasındaki gap küçükse overfitting kontrol altında demektir
- **Accuracy curve** — train ve val accuracy birlikte yükselip plato yaparsa ideal
- **Normalized CM** — diagonal değerleri yüksek, off-diagonal düşük

---

## 🧪 Test Scripti Uyumu

Hocaların `Test.txt` scripti:
- `read_predictions()` ile `<file> | predict:<int>` formatında dosya okuyor
- `class_labels = [1,2,3,4,5,6,7,8]` üzerinden confusion matrix ve classification_report üretiyor

`predict.py` çıktısı bu formatla **bire bir uyumludur**. Klasör adı→numara eşlemesi `train.py → CLASS_TO_LABEL` içinde tanımlı ve checkpoint dosyasında (`idx_to_label`) saklanır.

---

## 🛠️ Sorun Giderme

**"CUDA out of memory"** → `CONFIG["batch_size"]` değerini 16 veya 8'e düşürün.

**"Model boyutu 95 MB'ı geçti"** → MobileNetV3 ~17 MB; bu sınırı aşmamalı. Aşıyorsa `state_dict` yerine model nesnesini kaydetmiş olabilirsiniz; kodu olduğu gibi kullanın.

**Validation accuracy düşük kalıyor** →
1. Veri setini büyütün, sınıf dengesini kontrol edin
2. `CONFIG["epochs"]` artırın
3. Daha güçlü augmentation deneyin

**"Eğitim sırasında train acc yüksek, val acc düşük"** → Aşırı uyum (overfitting). Dropout'u artırın (0.3 → 0.5), `RandomErasing` olasılığını yükseltin, daha çok veri toplayın.
