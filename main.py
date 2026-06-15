from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys

# Backend'i sisteme tanıt
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))
from ai_engine import get_ai_response

app = FastAPI()
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