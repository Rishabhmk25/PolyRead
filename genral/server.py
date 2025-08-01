"""
server.py  – PolyRead backend (single-model version)

Features
────────
• POST /api/ocr        → run_ocr()  → {text, lines, image}
• POST /api/translate  → translate_text()  → {translated}
• POST /api/tts        → synthesize()  → audio file
• GET  /               → serves index.html + all static assets
"""
import logging, sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

import os
import uuid
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# ── your business-logic modules ────────────────────────────────
from ocr_module import run_ocr
from translate_module import translate_text_input
# from tts_module import synthesize_tts   # ← comment-out if you don’t have it

# ── FastAPI app setup ──────────────────────────────────────────
app = FastAPI(title="PolyRead API", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                   # tweak in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# static directory (index.html, app.js, css, images …)
STATIC_DIR = Path(__file__).parent / "static"


# ── helper: safe temp file save ────────────────────────────────
def _save_upload_tmp(upload: UploadFile) -> Path:
    suffix = Path(upload.filename).suffix or ".bin"
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(upload.file, tmp)
        return Path(tmp.name)

# ─────────────────────────  API ROUTES  ────────────────────────

@app.post("/api/ocr")
async def ocr_endpoint(request: Request,
                        file: UploadFile = File(...),
                        lang: str | None = None):

    tmp = _save_upload_tmp(file)
    try:
        raw_lines, img_path = run_ocr(str(tmp), lang=lang)   # pass str
    finally:
        tmp.unlink(missing_ok=True)

    # ---- make JSON-safe ---------------------------------------------------
    lines: list[str] = [
        x["text"] if isinstance(x, dict) and "text" in x else str(x)
        for x in raw_lines
     ]
    # ensure the outlined image really lives in ./static
    img_path = Path(img_path)
    target   = (STATIC_DIR / img_path.name)
    if img_path.exists() and img_path != target:
        img_path.replace(target)          # atomic move
    img_url: str = f"/static/{img_path.name}"
    # ----------------------------------------------------------------------

    return {
        "text": "\n".join(lines),
        "lines": lines,
        "image": img_url,
    }



@app.post("/api/translate")
async def translate_endpoint(payload: dict):
    """
    Payload: { "text": "...", "target_lang": "en" }
    """
    text = payload.get("text")
    #tgt  = payload.get("target_lang")
    if not text: # or not tgt:
        raise HTTPException(status_code=400, detail="text and target_lang required")

    try:
        # translate_module exposes translate_text_input(text)
        _, _, translated = translate_text_input(text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"translated": translated}


@app.post("/api/tts")
async def tts_endpoint(payload: dict):
    """
    Payload: { "text": "..." }
    Returns an MP3 file.
    """
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="text required")

    # path = synthesize_tts(text)       # uncomment when you have a TTS function
    # return FileResponse(path, media_type="audio/mpeg", filename="speech.mp3")
    raise HTTPException(status_code=501, detail="TTS not wired yet")


# ── serve static files (index.html, app.js, etc.) ──────────────
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

# ── ROUTE AUDIT – prints once at startup ───────────────────────
@app.on_event("startup")
async def show_routes() -> None:
    print("\n=== FastAPI ROUTES ===")
    for r in app.routes:
        if hasattr(r, "methods"):
            methods = ",".join(r.methods)
            print(f"{methods:<14} {r.path}")
    print("=== END ROUTES ===\n")
