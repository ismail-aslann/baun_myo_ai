import json
import os
import threading
import time
from collections import defaultdict, deque
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from backend import ai_engine
from backend.knowledge import summary

BASE_DIR = Path(__file__).resolve().parent
FRONTEND = BASE_DIR / "frontend"

RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MIN", "15"))

app = FastAPI(title="BAÜN MYO Asistan")
# Yalnızca frontend klasörü dışarı açılır (.env ve kaynak kodu sunulmaz).
app.mount("/static", StaticFiles(directory=FRONTEND), name="static")


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[dict] = Field(default_factory=list, max_length=60)

    @field_validator("message")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Mesaj boş olamaz")
        return v


_hits: dict[str, deque] = defaultdict(deque)
_hits_lock = threading.Lock()


def check_rate_limit(request: Request) -> None:
    """IP başına dakikada RATE_LIMIT istek (bellek içi, tek sunucu için yeterli)."""
    fwd = request.headers.get("x-forwarded-for", "")
    ip = fwd.split(",")[0].strip() or (request.client.host if request.client else "?")
    now = time.monotonic()
    with _hits_lock:
        q = _hits[ip]
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= RATE_LIMIT:
            raise HTTPException(status_code=429, detail="Çok fazla istek. Lütfen biraz bekleyin.")
        q.append(now)
        if len(_hits) > 10_000:  # bellek şişmesin
            for k in [k for k, v in _hits.items() if not v or now - v[-1] > 60]:
                del _hits[k]


@app.get("/")
async def index():
    return FileResponse(FRONTEND / "index.html")


@app.get("/api/health")
async def health():
    return {
        "ok": True,
        "model": ai_engine.MODEL,
        "key_configured": bool(os.getenv("OPENROUTER_API_KEY")),
        "knowledge": summary(),
    }


@app.post("/api/chat")
def chat_stream(data: ChatIn, request: Request):
    """Yanıtı Server-Sent Events olarak parça parça gönderir."""
    check_rate_limit(request)

    def events():
        try:
            for piece in ai_engine.stream_ai_response(data.message, data.history):
                yield f"data: {json.dumps({'t': piece}, ensure_ascii=False)}\n\n"
        except ai_engine.MissingKeyError as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        except Exception as e:  # noqa: BLE001
            print(f"HATA: {e!r}")
            yield f"data: {json.dumps({'error': 'Model şu an yanıt veremedi, biraz sonra tekrar deneyin.'}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/chat")
def chat(data: ChatIn, request: Request):
    """Eski istemciler için tek parça yanıt."""
    check_rate_limit(request)
    try:
        return {"response": ai_engine.get_ai_response(data.message, data.history)}
    except ai_engine.MissingKeyError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:  # noqa: BLE001
        print(f"HATA: {e!r}")
        raise HTTPException(status_code=502, detail="Model şu an yanıt veremedi.")
