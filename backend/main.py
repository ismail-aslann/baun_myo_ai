import sys
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Proje kök dizinini otomatik buluyoruz
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Backend klasörünü path'e ekliyoruz ki ai_engine'i bulsun
sys.path.append(os.path.join(BASE_DIR, "backend"))
from ai_engine import get_ai_response

app = FastAPI()

# Frontend klasörünü statik dosya olarak bağlıyoruz
# Dosya yapın: baun_myo_projesi/frontend
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend")), name="static")

# Ana sayfa isteği geldiğinde index.html'i gönderiyoruz
@app.get("/")
async def read_index():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "index.html"))

# Sohbet rotası
@app.post("/chat")
async def chat_endpoint(data: dict):
    user_message = data.get("message")
    # ai_engine içindeki fonksiyonu çağırıyoruz
    response = get_ai_response(user_message)
    return {"response": response}