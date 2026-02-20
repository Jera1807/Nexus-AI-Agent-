from fastapi import FastAPI

from src.config import settings

app = FastAPI(title="Nexus Agent", version="0.1.0")


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}
