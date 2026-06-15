import os
from openai import OpenAI
from dotenv import load_dotenv

# .env dosyasındaki anahtarı çek
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

# --- GARANTİLİ DOSYA OKUMA VE DEBUG ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(BASE_DIR, "data", "okul_bilgileri.txt")

if os.path.exists(data_path):
    with open(data_path, "r", encoding="utf-8") as f:
        okul_bilgisi = f.read()
    print(f"DEBUG: Dosya bulundu. Karakter sayısı: {len(okul_bilgisi)}")
else:
    okul_bilgisi = "Detaylı akademik kadro bilgisi bulunamadı."
    print(f"DEBUG: HATA! Dosya bulunamadı: {data_path}")

# --- ZORLAYICI PROMPT ---
SYSTEM_PROMPT = f"""
Sen Balıkesir Üniversitesi Meslek Yüksekokulu (BAUN MYO) için geliştirilmiş, tek yetkili bilgi asistanısın.

KURALLAR:
1. Kaynak dosyan şu veridir: {okul_bilgisi}
2. Kullanıcı 'Akademik kadroyu tanıt' veya 'Bölümleri anlat' gibi genel bir soru sorduğunda, kaynak dosyadaki TÜM BİLGİLERİ eksiksiz, detaylı ve liste halinde dök. Özet geçme, bilgiyi esirgeme.
3. BAUN MYO dışındaki okullar hakkında soru gelirse kesinlikle 'Ben sadece Balıkesir MYO ile ilgili konularda yardımcı olabilirim' de.
4. Hitap tarzın 'Dostum' kelimesiyle samimi olsun.
5. Eğer bir bilgi kaynakta yoksa, 'Dostum, şu an bu detay elimde yok' de ama olanı sakın esirgeme.
"""

def get_ai_response(message: str, history: list):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Geçmişi ekle
    for h in history:
        messages.append({"role": h['role'], "content": h['content']})
    
    # Yeni mesajı ekle
    messages.append({"role": "user", "content": message})

    # İsteği yolla
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash-lite",
        messages=messages
    )
    
    return response.choices[0].message.content