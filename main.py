from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys

# Backend klasörünü sisteme tanıt
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

# ÖNEMLİ: ai_engine'i burada bir try-except ile import edelim
try:
    from ai_engine import get_ai_response
except ImportError as e:
    print(f"IMPORT HATASI: {e}")
    get_ai_response = None

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "index.html"))

@app.post("/chat")
async def chat_endpoint(data: dict):
    if get_ai_response is None:
        raise HTTPException(status_code=500, detail="ai_engine yüklenemedi!")
    
    try:
        user_message = data.get("message", "")
        print(f"Gelen mesaj: {user_message}") # Loglara düşecek
        response = get_ai_response(user_message)
        return {"response": response}
    except Exception as e:
        print(f"DİREKT HATA: {str(e)}") # Render loglarında bu hatayı görmemiz lazım
        raise HTTPException(status_code=500, detail=str(e))