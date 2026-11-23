# BAÜN MYO Asistan

Balıkesir Üniversitesi Balıkesir Meslek Yüksekokulu için yapay zekâ destekli soru-cevap asistanı.
Balıkesir MYO Yapay Zekâ Operatörlüğü öğrencilerinin ekip projesidir; resmi bir okul hizmeti değildir.

- Backend: FastAPI (Python), model çağrısı OpenRouter üzerinden (varsayılan: `google/gemini-2.5-flash-lite`)
- Frontend: Tek sayfa HTML/CSS/JS, canlı akışlı yanıt, Markdown, karanlık mod, mobil uyumlu
- Bilgi paketi: `knowledge/` klasöründeki Markdown dosyaları (okulun resmi sitesinden derlendi)

## Kurulum

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env      # macOS/Linux: cp .env.example .env
```

`.env` içine OpenRouter anahtarını yazın (https://openrouter.ai/keys):

```
OPENROUTER_API_KEY=sk-or-...
```

Çalıştırma:

```bash
uvicorn main:app --reload
```

Tarayıcıda http://127.0.0.1:8000 adresini açın.

> **Anahtarları asla koda veya repoya yazmayın.** `.env` dosyası `.gitignore` içindedir.

## Bilgi paketini güncellemek

`knowledge/` klasöründeki her `.md` dosyası sırayla okunup modele kaynak olarak verilir.

| Dosya | İçerik |
|---|---|
| `01_genel_bilgiler.md` | Okul tanıtımı, tarihçe, misyon-vizyon |
| `02_yonetim.md` | Müdür, yardımcılar, yönetim kurulu, öğrenci temsilcisi |
| `03_bolumler_ve_programlar.md` | 16 bölüm, 20 program, bölüm siteleri, akreditasyon |
| `04_akademik_kadro.md` | Bölümlere göre akademisyenler, dahili numaralar, e-postalar |
| `05_idari_kadro.md` | İdari personel |
| `06_staj_ve_3arti1.md` | 3+1 işletmede mesleki eğitim, staj belgeleri |
| `07_ogrenci_islemleri.md` | Belge alma, sınav kuralları, SSS, faydalı bağlantılar |
| `08_iletisim.md` | Adres, telefon, e-posta |
| `09_ozel_yanitlar.md` | Ekibin hazır yanıtları |

Yeni bilgi eklemek için ilgili dosyayı düzenleyin ya da yeni bir `10_...md` dosyası ekleyin, ardından sunucuyu yeniden başlatın.
Her dosyanın başına kaynak sayfayı ve kontrol tarihini yazın.

## API

- `GET /api/health`: durum, model adı, anahtarın tanımlı olup olmadığı, yüklü bilgi dosyaları
- `POST /api/chat`: `{"message": "...", "history": [...]}`; yanıt Server-Sent Events olarak parça parça gelir
- `POST /chat`: aynı istek, tek parça JSON yanıt (`{"response": "..."}`)

## Yayınlama (Render)

Repo kökündeki `render.yaml` hazırdır. Render'da "New > Blueprint" ile repoyu seçin ve `OPENROUTER_API_KEY` değerini ortam değişkeni olarak girin.
