from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys

# Backend klasörünü path'e ekle ki ai_engine'i bulabilsin
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))
from ai_engine import get_ai_response

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Statik dosyaları bağla
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "index.html"))

@app.post("/chat")
async def chat_endpoint(data: dict):
    try:
        user_message = data.get("message")
        if not user_message:
            raise HTTPException(status_code=400, detail="Mesaj boş olamaz")
        
        response = get_ai_response(user_message)
        return {"response": response}
    except Exception as e:
        # Hata olursa 500 yerine detaylı log ver
        print(f"HATA: {str(e)}") 
        raise HTTPException(status_code=500, detail=str(e))