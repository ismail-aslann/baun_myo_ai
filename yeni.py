from google import genai

# Anahtarın artık cebimizde, sisteme dalıyoruz
client = genai.Client(api_key="AIzaSyDGe9ZNC6d5RQdmu1b5oUeSQ1qDKHqXzj8")

# Kendi döktüğün listedeki hafif siklet modeli kullanıyoruz!
response = client.models.generate_content(
    model='gemini-2.5-flash-lite',
    contents='Merhaba BAUN-MYO Asistanı, sistem devrede mi?'
)

print(response.text)