from fastapi import APIRouter, Query
from typing import List
from app.models.schemas import MASIDataPoint
from app.utils.data_loader import DataLoader
from app.utils.config import PERIODS

router = APIRouter(prefix="/api/masi", tags=["MASI"])


@router.get("/data", response_model=List[MASIDataPoint])
def get_masi_data(period: str = Query("6M", description="Période: 1M, 3M, 6M, 1Y, 2Y")):
    """
    Récupère les données MASI pour une période donnée.
    
    - **period**: Période (1M, 3M, 6M, 1Y, 2Y)
    """
    if period not in PERIODS:
        return {"error": f"Période invalide. Options: {list(PERIODS.keys())}"}
    
    try:
        df = DataLoader.load_masi_data()
        days = PERIODS[period]
        filtered_df = DataLoader.filter_by_period(df, days)
        return DataLoader.get_masi_list(filtered_df)
    except FileNotFoundError as e:
        return {"error": str(e)}


@router.get("/latest", response_model=MASIDataPoint)
def get_masi_latest():
    """
    Récupère la dernière valeur MASI disponible.
    """
    try:
        df = DataLoader.load_masi_data()
        if df.empty:
            return {"error": "Aucune donnée disponible"}
        latest = df.iloc[-1]
        return MASIDataPoint(
            date=latest["Date"],
            value=float(latest.get("Valeur", latest.get("Close", 0))),
            variation=float(latest.get("Variation %", None)) if "Variation %" in latest else None,
        )
    except FileNotFoundError as e:
        return {"error": str(e)}


@router.get("/stats")
def get_masi_stats(period: str = Query("6M", description="Période: 1M, 3M, 6M, 1Y, 2Y")):
    """
    Récupère les statistiques MASI pour une période donnée.
    """
    if period not in PERIODS:
        return {"error": f"Période invalide. Options: {list(PERIODS.keys())}"}
    
    try:
        df = DataLoader.load_masi_data()
        days = PERIODS[period]
        filtered_df = DataLoader.filter_by_period(df, days)
        
        if filtered_df.empty:
            return {"error": "Aucune donnée pour cette période"}
        
        values = filtered_df.get("Valeur", filtered_df.get("Close", []))
        
        return {
            "period": period,
            "min": float(values.min()),
            "max": float(values.max()),
            "mean": float(values.mean()),
            "std": float(values.std()),
            "current": float(filtered_df.iloc[-1].get("Valeur", filtered_df.iloc[-1].get("Close", 0))),
            "change_percent": float(
                ((filtered_df.iloc[-1].get("Valeur", filtered_df.iloc[-1].get("Close", 0)) - filtered_df.iloc[0].get("Valeur", filtered_df.iloc[0].get("Close", 0))) 
                 / filtered_df.iloc[0].get("Valeur", filtered_df.iloc[0].get("Close", 0))) * 100
            ),
        }
    except FileNotFoundError as e:
        return {"error": str(e)}
