from fastapi import APIRouter, Query
from typing import List
from app.models.schemas import VolatilityDataPoint, DashboardStats
from app.utils.data_loader import DataLoader
from app.utils.config import PERIODS, DATA_DIR
from datetime import datetime
import subprocess
import sys
from fastapi import HTTPException
import math
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/api/volatility", tags=["Volatility"])


@router.get("/data", response_model=List[VolatilityDataPoint])
def get_volatility_data(period: str = Query("6M", description="Période: 1M, 3M, 6M, 1Y, 2Y")):
    """
    Récupère les données de volatilité pour une période donnée.
    
    - **period**: Période (1M, 3M, 6M, 1Y, 2Y)
    """
    if period not in PERIODS:
        return {"error": f"Période invalide. Options: {list(PERIODS.keys())}"}
    
    try:
        df = DataLoader.load_volatility_data()
        days = PERIODS[period]
        filtered_df = DataLoader.filter_by_period(df, days)
        return DataLoader.get_volatility_list(filtered_df)
    except FileNotFoundError as e:
        return {"error": str(e)}


@router.get("/forecast")
def get_volatility_forecast():
    """
    Récupère la prévision de volatilité (2 prochaines semaines).
    """
    try:
        df = DataLoader.load_volatility_data()
        if df.empty:
            return {"error": "Aucune donnée disponible"}
        
        latest = df.iloc[-1]
        return {
            "forecast_date": latest["Date"].isoformat(),
            "volatility_2w": float(latest.get("vol_future_2w", None)) if "vol_future_2w" in latest else None,
            "garch_vol": float(latest.get("garch_vol", None)) if "garch_vol" in latest else None,
            "confidence": "high" if "garch_vol" in latest else "medium",
        }
    except FileNotFoundError as e:
        return {"error": str(e)}


@router.get("/dashboard-stats", response_model=DashboardStats)
def get_dashboard_stats(period: str = Query("6M", description="Période: 1M, 3M, 6M, 1Y, 2Y")):
    """
    Récupère les statistiques du tableau de bord (MASI + OPCVM).
    """
    if period not in PERIODS:
        return {"error": f"Période invalide. Options: {list(PERIODS.keys())}"}
    
    try:
        # Charger les données
        masi_df = DataLoader.load_masi_data()
        opcvm_df = DataLoader.load_opcvm_data()
        
        days = PERIODS[period]
        masi_filtered = DataLoader.filter_by_period(masi_df, days)
        opcvm_filtered = DataLoader.filter_by_period(opcvm_df, days)
        
        if masi_filtered.empty or opcvm_filtered.empty:
            return {"error": "Données insuffisantes pour cette période"}
        
        # Derniers points
        masi_latest = masi_filtered.iloc[-1]
        masi_first = masi_filtered.iloc[0]
        
        opcvm_latest = opcvm_filtered.iloc[-1]
        opcvm_first = opcvm_filtered.iloc[0]
        
        # Calcul des variations
        masi_value = float(masi_latest.get("Valeur", masi_latest.get("Close", 0)))
        masi_first_value = float(masi_first.get("Valeur", masi_first.get("Close", 0)))
        masi_change = ((masi_value - masi_first_value) / masi_first_value * 100) if masi_first_value != 0 else 0
        
        opcvm_value = float(opcvm_latest.get("Valeur Liquidative", opcvm_latest.get("Value", 0)))
        opcvm_first_value = float(opcvm_first.get("Valeur Liquidative", opcvm_first.get("Value", 0)))
        opcvm_change = ((opcvm_value - opcvm_first_value) / opcvm_first_value * 100) if opcvm_first_value != 0 else 0
        
        return DashboardStats(
            current_masi=masi_value,
            current_opcvm=opcvm_value,
            masi_change_percent=masi_change,
            opcvm_change_percent=opcvm_change,
            period=period,
            last_update=datetime.now(),
        )
    except FileNotFoundError as e:
        return {"error": str(e)}


@router.post("/run-modelling")
def run_modelling_script(timeout: int = 120):
    script_cwd = DATA_DIR

    try:
        proc = subprocess.run(
            [sys.executable, "modelling.py"],
            cwd=str(script_cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if proc.returncode != 0:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "stage": "execution",
                    "stderr": proc.stderr,
                    "stdout": proc.stdout,
                },
            )

    except subprocess.TimeoutExpired:
        return JSONResponse(
            status_code=504,
            content={"status": "error", "stage": "timeout"},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "stage": "exception", "message": str(e)},
        )

    # Chargement du résultat
    try:
        DataLoader._volatility_cache = None
        df = DataLoader.load_volatility_data()

        if df.empty:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "stage": "empty_dataset"},
            )

        latest = df.iloc[-1]

        return {
            "status": "success",
            "date": str(latest.get("Date")),
            "vol_future_2w_1": float(latest.get("vol_future_2w_1", None))*100,
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "stage": "post_processing", "message": str(e)},
        )
