from fastapi import FastAPI
from fastapi.responses import FileResponse
import pathlib

ROOT = pathlib.Path(__file__).parent
app = FastAPI()

@app.get("/")
def index():
    return FileResponse(ROOT / "Index.html")

@app.get("/{asset_path:path}")
def assets(asset_path: str):
    return FileResponse(ROOT / asset_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
