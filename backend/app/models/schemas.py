from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MASIDataPoint(BaseModel):
    """Schéma pour un point de données MASI"""
    date: datetime
    value: float
    variation: Optional[float] = None


class OPCVMDataPoint(BaseModel):
    """Schéma pour un point de données OPCVM Attijari"""
    date: datetime
    value: float
    performance_1w: Optional[float] = None
    performance_1m: Optional[float] = None
    performance_6m: Optional[float] = None
    performance_1y: Optional[float] = None


class VolatilityDataPoint(BaseModel):
    """Schéma pour un point de données de volatilité"""
    date: datetime
    garch_vol: Optional[float] = None
    vol_future_2w: Optional[float] = None
    performances_1w: Optional[float] = None
    variation: Optional[float] = None


class PeriodResponse(BaseModel):
    """Réponse pour les données d'une période"""
    period: str
    start_date: datetime
    end_date: datetime
    data_points: int


class DashboardStats(BaseModel):
    """Statistiques du tableau de bord"""
    current_masi: float
    current_opcvm: float
    masi_change_percent: float
    opcvm_change_percent: float
    period: str
    last_update: datetime
