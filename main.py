import os
import sys
# Proje kök dizinini sisteme ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
# Artık doğrudan import edebilirsin çünkü kök dizini ekledik
from backend.ai_engine import get_ai_response

app = FastAPI()
# ... kodun kalanı aynı kalsın ...
# app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "index.html"))

@app.post("/chat")
async def chat_endpoint(data: dict):
    try:
        user_message = data.get("message", "")
        # Frontend'den gelen 'history'yi alıyoruz, yoksa boş liste veriyoruz
        history = data.get("history", []) 
        
        # Fonksiyonuna hem mesajı hem de geçmişi gönderiyoruz
        response = get_ai_response(user_message, history)
        return {"response": response}
    except Exception as e:
        print(f"HATA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))