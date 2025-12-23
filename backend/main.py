from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.config import APP_TITLE, APP_VERSION, APP_DESCRIPTION, CORS_ORIGINS
from app.routes import masi, opcvm, volatility, final_dataset

# Initialiser l'application FastAPI
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(masi.router)
app.include_router(opcvm.router)
app.include_router(volatility.router)
app.include_router(final_dataset.router)


@app.get("/", tags=["Health"])
def read_root():
    """Endpoint de santé de l'API"""
    return {
        "status": "healthy",
        "app_name": APP_TITLE,
        "version": APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Vérification de l'état de l'API"""
    return {
        "status": "ok",
        "message": "API est fonctionnelle",
    }
