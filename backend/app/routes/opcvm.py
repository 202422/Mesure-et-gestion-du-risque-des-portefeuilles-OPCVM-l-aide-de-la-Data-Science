from fastapi import APIRouter, Query
from typing import List
from app.models.schemas import OPCVMDataPoint
from app.utils.data_loader import DataLoader
from app.utils.config import PERIODS

router = APIRouter(prefix="/api/opcvm", tags=["OPCVM"])


@router.get("/data", response_model=List[OPCVMDataPoint])
def get_opcvm_data(period: str = Query("6M", description="Période: 1M, 3M, 6M, 1Y, 2Y")):
    """
    Récupère les données OPCVM Attijari pour une période donnée.
    
    - **period**: Période (1M, 3M, 6M, 1Y, 2Y)
    """
    if period not in PERIODS:
        return {"error": f"Période invalide. Options: {list(PERIODS.keys())}"}
    
    try:
        df = DataLoader.load_opcvm_data()
        days = PERIODS[period]
        filtered_df = DataLoader.filter_by_period(df, days)
        return DataLoader.get_opcvm_list(filtered_df)
    except FileNotFoundError as e:
        return {"error": str(e)}


@router.get("/latest", response_model=OPCVMDataPoint)
def get_opcvm_latest():
    """
    Récupère la dernière valeur OPCVM Attijari disponible.
    """
    try:
        df = DataLoader.load_opcvm_data()
        if df.empty:
            return {"error": "Aucune donnée disponible"}
        latest = df.iloc[-1]
        return OPCVMDataPoint(
            date=latest["Date"],
            value=float(latest.get("Valeur Liquidative", latest.get("Value", 0))),
            performance_1w=float(latest.get("Performances glissantes 1 semaine", None)) if "Performances glissantes 1 semaine" in latest else None,
            performance_1m=float(latest.get("Performances glissantes Depuis Début d'année", None)) if "Performances glissantes Depuis Début d'année" in latest else None,
            performance_6m=float(latest.get("Performances glissantes 6 mois", None)) if "Performances glissantes 6 mois" in latest else None,
            performance_1y=float(latest.get("Performances glissantes 1 an", None)) if "Performances glissantes 1 an" in latest else None,
        )
    except FileNotFoundError as e:
        return {"error": str(e)}


@router.get("/stats")
def get_opcvm_stats(period: str = Query("6M", description="Période: 1M, 3M, 6M, 1Y, 2Y")):
    """
    Récupère les statistiques OPCVM pour une période donnée.
    """
    if period not in PERIODS:
        return {"error": f"Période invalide. Options: {list(PERIODS.keys())}"}
    
    try:
        df = DataLoader.load_opcvm_data()
        days = PERIODS[period]
        filtered_df = DataLoader.filter_by_period(df, days)
        
        if filtered_df.empty:
            return {"error": "Aucune donnée pour cette période"}
        
        values = filtered_df.get("Valeur Liquidative", filtered_df.get("Value", []))
        
        return {
            "period": period,
            "min": float(values.min()),
            "max": float(values.max()),
            "mean": float(values.mean()),
            "std": float(values.std()),
            "current": float(filtered_df.iloc[-1].get("Valeur Liquidative", filtered_df.iloc[-1].get("Value", 0))),
            "change_percent": float(
                ((filtered_df.iloc[-1].get("Valeur Liquidative", filtered_df.iloc[-1].get("Value", 0)) - filtered_df.iloc[0].get("Valeur Liquidative", filtered_df.iloc[0].get("Value", 0))) 
                 / filtered_df.iloc[0].get("Valeur Liquidative", filtered_df.iloc[0].get("Value", 0))) * 100
            ),
        }
    except FileNotFoundError as e:
        return {"error": str(e)}
