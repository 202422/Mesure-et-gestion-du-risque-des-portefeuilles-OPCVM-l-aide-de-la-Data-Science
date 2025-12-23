from fastapi import APIRouter, HTTPException
from typing import List
import math
from app.utils.data_loader import DataLoader
from app.models.schemas import OPCVMDataPoint, MASIDataPoint

router = APIRouter(prefix="/api/final", tags=["FinalDataset"])


@router.get("/opcvm_liquidative", response_model=List[OPCVMDataPoint])
def get_opcvm_liquidative():
    """Retourne la série complète `Date` / `Valeur Liquidative` depuis `final_dataset.csv`."""
    try:
        df = DataLoader.load_final_dataset()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if df.empty:
        return []

    result: List[OPCVMDataPoint] = []
    # Iterate rows and map 'Date' -> date, 'Valeur Liquidative' -> value
    for _, row in df.iterrows():
        value = row.get("Valeur Liquidative", None)
        try:
            v = float(value) if value is not None and value != "" else 0.0
        except Exception:
            v = 0.0

        result.append(OPCVMDataPoint(date=row["Date"], value=v))

    return result


@router.get("/masi_weekly_mean", response_model=List[MASIDataPoint])
def get_masi_weekly_mean():
    """Retourne la série complète `Date` / `weekly_mean` (MASI) depuis `final_dataset.csv`."""
    try:
        df = DataLoader.load_final_dataset()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if df.empty:
        return []

    result: List[MASIDataPoint] = []
    for _, row in df.iterrows():
        value = row.get("weekly_mean", None)
        try:
            v = float(value) if value is not None and value != "" else 0.0
        except Exception:
            v = 0.0

        # Extract variation if it exists and is valid
        variation = row.get("Variation %", None)
        var = None
        try:
            if variation is not None and variation != "":
                v_float = float(variation)
                # Check if value is NaN or Inf
                if not (math.isnan(v_float) or math.isinf(v_float)):
                    var = v_float
        except Exception:
            var = None

        result.append(MASIDataPoint(date=row["Date"], value=v, variation=var))

    return result
