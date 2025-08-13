from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .routers import auth as auth_router

s = get_settings()
app = FastAPI(title="Auth Service")

origins = ["*"] if s.CORS_ORIGINS == "*" else [o.strip() for o in s.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

app.include_router(auth_router.router)
