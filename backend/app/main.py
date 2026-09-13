from fastapi import FastAPI

from backend.app.api.agent import router as agent_router


app = FastAPI(
    title="Hiver Support Intelligence",
    version="1.0.0",
)

app.include_router(agent_router)


@app.get("/health")
def health():
    return {"status": "ok"}