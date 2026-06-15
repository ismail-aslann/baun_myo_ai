import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

# VERİ KISMI (Burada süslü parantezleri temizledim)
OKUL_VERISI = """
BAÜN MERKEZ MESLEK YÜKSEKOKULU (BAUN MYO) – GÜNCEL BİLGİLENDİRME
1. GENEL BİLGİLER VE KONUM
Okulun Adı: Balıkesir Üniversitesi Balıkesir Meslek Yüksekokulu (BAUN Merkez MYO)
Konum: Çağış Yerleşkesi, Altıeylül / Balıkesir
Web Sitesi: https://balikesirmyo.balikesir.edu.tr/

2. YÖNETİM
Müdür: Doç. Dr. Fatmagül TOLUN
Müdür Yardımcıları: Öğr. Gör. Özgür YILMAZ, Dr. Öğr. Üyesi Fulya GÜNGÖR
Yüksekokul Sekreteri: Davut KESGİN

3. STAJ VE EĞİTİM MODELİ (3+1 SİSTEMİ)
3+1 Uygulanan Programlar: Çocuk Gelişimi, Grafik Tasarımı, İnşaat Teknolojisi, İşletme Yönetimi, Makine, Turizm ve Otel İşletmeciliği, Yapay Zekâ Operatörlüğü (YZO).
Bu programlarda öğrenciler 3 dönem okulda, 4. dönem işletmede eğitim görür. Diğerlerinde klasik yaz stajı vardır.

4. BÖLÜMLER (20 PROGRAM)
Bilgisayar Programcılığı, Büro Yönetimi ve Yönetici Asistanlığı, Çocuk Gelişimi, Elektrik, Elektronik Haberleşme Teknolojisi, Elektronik Teknolojisi, Geleneksel El Sanatları, Grafik Tasarımı, İklimlendirme ve Soğutma Teknolojisi, İnşaat Teknolojisi, İşletme Yönetimi, Kontrol ve Otomasyon Teknolojisi, Madencilik Teknolojisi, Makine, Muhasebe ve Vergi Uygulamaları, Otomotiv Teknolojisi, Pazarlama, Tekstil Teknolojisi, Turizm ve Otel İşletmeciliği, Yapay Zekâ Operatörlüğü (YZO).

5. AKADEMİK KADRO
Yönetim: Doç. Dr. Fatmagül TOLUN, Özgür YILMAZ, Fulya GÜNGÖR.
Profesörler: Prof. Dr. Ferihan GÖKTEPE, Prof. Dr. İlhan GÜLGÖNÜL, Prof. Dr. Nurcihan CERYAN, Prof. Dr. Kudret GÜL.
Doçentler: Doç. Dr. Pınar ERKAL, Doç. Dr. Hakan ÇITAK, Doç. Dr. Mehmet Can TOKMAK, Doç. Dr. Fulya GÜNGÖR.
(Kadro listesi dosyadaki isimlerle aynıdır.)

6. ILETISIM
Telefon: (0266) 612 12 09 | E-posta: myo@balikesir.edu.tr | Adres: Çağış Yerleşkesi, Altıeylül/Balıkesir
"""

SYSTEM_PROMPT = f"""
Sen Balıkesir Üniversitesi Meslek Yüksekokulu (BAUN MYO) için geliştirilmiş, tek yetkili bilgi asistanısın.

KAYNAK BİLGİLERİN:
{OKUL_VERISI}

KURALLAR:
1. Sadece yukarıdaki 'KAYNAK BİLGİLERİN' kısmındaki bilgileri baz al.
2. Kullanıcı ne sorarsa sorsun (bölümler, akademik kadro, 3+1 sistemi), cevabını bu kaynaktan bul ve eksiksiz ver. 
3. Bilgi kaynakta yoksa 'Dostum, şu an bu detay elimde yok' de.
4. BAUN MYO dışındaki soruları reddet.
5. Hitap tarzın samimi ve 'Dostum' kelimesiyle desteklenmiş olsun.
"""

def get_ai_response(message: str, history: list):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history:
        messages.append({"role": h['role'], "content": h['content']})
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash-lite",
        messages=messages,
        temperature=0.1
    )
    return response.choices[0].message.content