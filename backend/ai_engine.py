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

# Okul bilgisini çek
try:
    with open("../data/okul_bilgileri.txt", "r", encoding="utf-8") as f:
        okul_bilgisi = f.read()
except:
    okul_bilgisi = "Okul bilgisi bulunamadı."

# İsmo, bak buraya ekledik promptu, bir daha kaybolmasın!
SYSTEM_PROMPT = f"""
Sen Balıkesir Üniversitesi Meslek Yüksekokulu (BAUN MYO) için geliştirilmiş, çok yönlü bir asistansın.

ÖNCELİK SIRALAMASI:
1. Sen bir BAUN MYO bilgi asistanısın. Okul ile ilgili bilgileri {okul_bilgisi} kaynağından kesinlikle kullan.
2. Ayrıca bir yazılımcı, matematikçi ve genel kültür uzmanısın.
3. 'Naber', 'Nasılsın' gibi sorulara sıcak bir şekilde 'Dostum' diyerek cevap ver.
4. Kod yazman istenirse tereddüt etme, temiz kod yaz.
5. Matematiksel işlemleri anında yap ve sonucu net ver.
6. Eğer soru okulun uzmanlık alanı dışındaysa: "Dostum, bu konu uzmanlık alanım olan BAUN MYO dışında ama yine de bildiğim kadarıyla söyleyeyim..." diyerek cevapla.
7. Bilmediğin bir şey olursa asla uydurma, 'Bilgim yok' de.

Hitap tarzın her zaman samimi, yardımsever ve 'Dostum' kelimesiyle desteklenmiş olsun.
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