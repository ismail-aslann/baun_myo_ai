import os
from openai import OpenAI
from dotenv import load_dotenv

# .env ayarları
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

# --- %100 GARANTİLİ YOL BULUCU VE OKUYUCU ---
# Dosyanın olduğu yer neresi olursa olsun, kök dizindeki data/ klasörünü bulur.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Eğer backend klasörünün içinde çalışıyorsak bir üst dizine çık
if "backend" in BASE_DIR:
    BASE_DIR = os.path.dirname(BASE_DIR)

data_path = os.path.join(BASE_DIR, "data", "okul_bilgileri.txt")

if os.path.exists(data_path):
    with open(data_path, "r", encoding="utf-8") as f:
        okul_bilgisi = f.read()
    print(f"DEBUG_SUCCESS: Dosya okundu. Yol: {data_path}")
else:
    okul_bilgisi = "Bilgi bulunamadı."
    print(f"DEBUG_ERROR: DOSYA BULUNAMADI! Aranan yol: {data_path}")

# --- ZORLAYICI PROMPT ---
SYSTEM_PROMPT = f"""
Sen Balıkesir Üniversitesi Meslek Yüksekokulu (BAUN MYO) için geliştirilmiş, tek yetkili bilgi asistanısın.

KURALLAR:
1. Kaynak dosyan şu veridir: {okul_bilgisi}
2. Kullanıcı her türlü soru sorduğunda, kaynak dosyadaki bilgileri referans al. Eğer bilgi dosyada varsa, detayıyla dök. 
3. Dosyada bilgi yoksa uydurma, 'Dostum, şu an bu detay elimde yok' de.
4. BAUN MYO dışındaki okullar hakkında soru gelirse kesinlikle 'Ben sadece Balıkesir MYO ile ilgili konularda yardımcı olabilirim' de.
5. Hitap tarzın 'Dostum' kelimesiyle samimi olsun.
"""

def get_ai_response(message: str, history: list):
    # Sistemi kuruyoruz
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"REFERANS BİLGİ: {okul_bilgisi}"}
    ]
    
    # Geçmişi ekle
    for h in history:
        messages.append({"role": h['role'], "content": h['content']})
    
    # Yeni mesajı ekle
    messages.append({"role": "user", "content": message})

    # İsteği yolla (Daha kesin cevaplar için temperature 0.1)
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash-lite",
        messages=messages,
        temperature=0.1
    )
    
    return response.choices[0].message.content