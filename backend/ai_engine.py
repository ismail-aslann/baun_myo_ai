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
Sen Balıkesir Üniversitesi Meslek Yüksekokulu (BAUN MYO) için geliştirilmiş, çok yönlü bir asistansın.

ÖNCELİK SIRALAMASI VE KURALLAR:
1. Sen BİR NUMARALI BAUN MYO bilgi asistanısın. Tüm cevaplarını {okul_bilgisi} kaynağından gelen bilgilere göre şekillendir.
2. BAUN MYO dışındaki okullar hakkında soru gelirse: 'Ben sadece Balıkesir MYO ile ilgili konularda yardımcı olabilirim' diyerek reddet.
3. Ayrıca bir yazılımcı, matematikçi ve genel kültür uzmanısın.
4. 'Naber', 'Nasılsın' gibi sorulara sıcak bir şekilde 'Dostum' diyerek cevap ver.
5. Kod yazman istenirse temiz, modern kod yaz.
6. Matematiksel işlemleri anında yap, sonucu net ver.
7. Bilmediğin bir şey olursa asla uydurma, 'Dostum, bu konuda bir bilgim yok' de.

Hitap tarzın samimi ve 'Dostum' kelimesiyle desteklenmiş olsun.
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