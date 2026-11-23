"""API anahtarı olmadan arayüzü denemek için: modeli sahte, akışlı bir yanıtla değiştirir.

Kullanım:  python tests/fake_server.py   (http://127.0.0.1:8765)
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("OPENROUTER_API_KEY", "fake-key-for-ui-testing")

import uvicorn  # noqa: E402

import main  # noqa: E402
from backend import ai_engine  # noqa: E402

DEMO = """Tabii! **Balıkesir MYO yönetimi** şöyle:

| Görev | Ad Soyad | Dahili |
|---|---|---|
| Müdür | Doç. Dr. Fatmagül TOLUN | 221066 |
| Müdür Yardımcısı | Öğr. Gör. Özgür YILMAZ | 221082 |
| Müdür Yardımcısı | Dr. Öğr. Üyesi Fulya GÜNGÖR | 221077 |

- Santral: `0266 612 12 09`
- E-posta: myo@balikesir.edu.tr

<img src=x onerror="alert('xss')"> bu satırdaki HTML temizlenmeli.

Kaynak: https://balikesirmyo.balikesir.edu.tr/yonetim
"""


def fake_stream(message, history):
    for i in range(0, len(DEMO), 12):
        time.sleep(0.03)
        yield DEMO[i:i + 12]


ai_engine.stream_ai_response = fake_stream

if __name__ == "__main__":
    uvicorn.run(main.app, host="127.0.0.1", port=8765)
