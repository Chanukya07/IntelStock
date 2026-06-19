"""FastAPI application entrypoint for IntelStock."""

from fastapi import FastAPI

from backend.api.routes import router

app = FastAPI(title="IntelStock API", version="0.1.0")
app.include_router(router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
