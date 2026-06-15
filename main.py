from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from backend.ai_engine import get_ai_response

app = FastAPI()

# Kök dizini (baun_myo_projesi klasörü) alıyoruz
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Frontend klasörünü kök dizin altından bağlıyoruz
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend")), name="static")

# Ana sayfa: Kök dizindeki frontend klasörünün içindeki index.html
@app.get("/")
async def read_index():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "index.html"))

# Sohbet rotası
@app.post("/chat")
async def chat_endpoint(data: dict):
    user_message = data.get("message")
    # ai_engine artık backend klasörünün içinde olduğu için import yolu güncellendi
    response = get_ai_response(user_message)
    return {"response": response}