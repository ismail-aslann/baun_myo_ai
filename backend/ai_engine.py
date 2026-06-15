import os
from openai import OpenAI
from dotenv import load_dotenv

# .env dosyasındaki anahtarı çek
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# OpenRouter istemcisini kur
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

# OKUL BİLGİSİNİ KÖK DİZİNDEN ÇEK (Yol düzeltildi!)
try:
    with open("data/okul_bilgileri.txt", "r", encoding="utf-8") as f:
        okul_bilgisi = f.read()
except:
    okul_bilgisi = "Okul bilgisi bulunamadı."

SYSTEM_PROMPT = f"""
Sen Balıkesir Üniversitesi Meslek Yüksekokulu (BAUN MYO) için geliştirilmiş, tek yetkili bilgi asistanısın.

KURALLAR:
1. Kaynak dosyan şu: {okul_bilgisi}
2. Kullanıcı 'Akademik kadroyu tanıt' gibi genel bir soru sorduğunda, elindeki bilgilerden tüm bölümlerin akademik kadrosunu özetleyerek ver. Soru sormasını bekleme, elindeki bilgiyi hemen dök.
3. BAUN MYO dışındaki okullar hakkında soru gelirse kesinlikle 'Ben sadece Balıkesir MYO ile ilgili konularda yardımcı olabilirim' de.
4. Hitap tarzın 'Dostum' kelimesiyle samimi olsun.
5. Eğer bir bilgi eksikse, 'Dostum, şu an bu detay elimde yok' de ama olanı sakın esirgeme.
"""

def get_ai_response(message: str, history: list):
    # Sistemi kuruyoruz
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