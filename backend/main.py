import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_engine import get_ai_response
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from ai_engine import get_ai_response # Engine'den çekiyoruz

app = FastAPI(title="BAUN-MYO AI Backend (Final Modüler)", version="8.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class HistoryItem(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[HistoryItem]] = []

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        # Pydantic objesini dict listesine çevirip engine'e yolla
        history_dicts = [{"role": h.role, "content": h.content} for h in req.history]
        
        reply = get_ai_response(req.message, history_dicts)
        
        return {"type": "text", "reply": reply}
    except Exception as e:
        print(f"BABA HATA ŞURADA: {e}") # Bunu terminalde gör
        return {"type": "text", "reply": f"Hata: {str(e)}"}