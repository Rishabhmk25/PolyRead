from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import pathlib, shutil
from st import pipeline

ROOT = pathlib.Path(__file__).parent
app  = FastAPI()
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
def html():
    return FileResponse(ROOT / "Index.html")

@app.get("/{path:path}")
def assets(path:str):
    return FileResponse(ROOT / path)

@app.post("/api/model2")
async def structure_ocr(file: UploadFile = File(...)):
    # ... (existing saving & pipeline.predict)
    md_path = ROOT / "output" / f"{tmp.stem}.md"
    markdown = md_path.read_text(encoding="utf-8") if md_path.exists() else ""

    # save a quick PNG so /output/<name>.png is available if you want
    preview_png = ROOT / "output" / f"{tmp.stem}_preview.png"
    pipeline.save_visualization(str(tmp), preview_png)   # or whatever helper you prefer

    return JSONResponse({
        "markdown": markdown,
        "image": f"/output/{preview_png.name}",
        "lines": []          # keeps frontend happy
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
