from pathlib import Path
import os

# Chemin de base du backend (dans Docker : /app)
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # remonte 3 niveaux jusqu'à /app

# Chemins vers les fichiers de données CSV
DATA_DIR = BASE_DIR / "data"
MASI_FILE = DATA_DIR / "MASI_combined.csv"
OPCVM_FILE = DATA_DIR / "attijari_diversifie.csv"
VOLATILITY_FILE = DATA_DIR / "volatility_forecasted_dataset.csv"
FINAL_DATASET_FILE = DATA_DIR / "final_dataset.csv"

# Configuration FastAPI
APP_TITLE = "Financial Data API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "API pour les données financières MASI et OPCVM Attijari"

# Configuration CORS 
CORS_ORIGINS = [ 
    "http://localhost:3000", 
    "http://localhost:8000", 
    "http://127.0.0.1:3000", 
    "http://127.0.0.1:8000", 
    ]

# Périodes disponibles
PERIODS = {
    "1M": 30,
    "3M": 90,
    "6M": 180,
    "1Y": 365,
    "2Y": 730,
}
