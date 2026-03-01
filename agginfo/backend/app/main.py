from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .schemas import StatRecord
from .services.estat_client import EstatClient
from .themes import THEMES

load_dotenv()

app = FastAPI(title="AggInfo JP Stats")
client = EstatClient()

frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/assets", StaticFiles(directory=str(frontend_dir)), name="assets")


@app.get("/", response_class=FileResponse)
def root() -> FileResponse:
    return FileResponse(frontend_dir / "index.html")


@app.get("/api/themes")
def get_themes() -> list[dict[str, str]]:
    return [{"key": t.key, "label": t.label} for t in THEMES.values()]


@app.get("/api/stats", response_model=list[StatRecord])
async def get_stats(
    theme: str = Query(default="population"),
    pref: str | None = Query(default=None),
    years: int = Query(default=20, ge=1, le=50),
) -> list[StatRecord]:
    try:
        return await client.fetch(theme=theme, pref=pref, years=years)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"fetch failed: {exc}") from exc
