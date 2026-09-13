from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.agent import router as agent_router
from backend.app.api.auth import router as auth_router


app = FastAPI(
    title="Hiver Support Intelligence",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_router)
app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok"}