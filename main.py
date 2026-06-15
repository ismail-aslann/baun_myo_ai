from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
# Backend klasörün kökte olduğu için bu import kesin çalışır
from backend.ai_engine import get_ai_response

app = FastAPI()

# Projenin en ana klasörünü (baun_myo_projesi) çalışma dizini yapıyoruz
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Bu satır, projedeki her şeyi /static adresine bağlar
# Yani /static/frontend/style.css dediğinde frontend klasörünü görür
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")

@app.get("/")
async def read_index():
    # index.html dosyasını frontend klasöründen çeker
    return FileResponse(os.path.join(BASE_DIR, "frontend", "index.html"))

@app.post("/chat")
async def chat_endpoint(data: dict):
    # Kullanıcıdan gelen mesajı ai_engine'e gönderir
    message = data.get("message", "")
    response = get_ai_response(message)
    return {"response": response}