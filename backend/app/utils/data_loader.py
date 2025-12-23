import pandas as pd
from typing import List, Tuple
from datetime import datetime, timedelta
from app.models.schemas import MASIDataPoint, OPCVMDataPoint, VolatilityDataPoint
from app.utils.config import MASI_FILE, OPCVM_FILE, VOLATILITY_FILE, FINAL_DATASET_FILE


class DataLoader:
    """Classe pour charger et traiter les données CSV"""

    _masi_cache = None
    _opcvm_cache = None
    _volatility_cache = None
    _final_dataset_cache = None

    @classmethod
    def load_masi_data(cls) -> pd.DataFrame:
        """Charge les données MASI avec cache"""
        if cls._masi_cache is None:
            if MASI_FILE.exists():
                cls._masi_cache = pd.read_csv(MASI_FILE, parse_dates=["Date"])
                cls._masi_cache["Date"] = pd.to_datetime(cls._masi_cache["Date"])
                cls._masi_cache = cls._masi_cache.sort_values("Date")
            else:
                raise FileNotFoundError(f"Fichier MASI non trouvé: {MASI_FILE}")
        return cls._masi_cache.copy()

    @classmethod
    def load_opcvm_data(cls) -> pd.DataFrame:
        """Charge les données OPCVM Attijari avec cache"""
        if cls._opcvm_cache is None:
            if OPCVM_FILE.exists():
                cls._opcvm_cache = pd.read_csv(OPCVM_FILE, parse_dates=["Date"])
                cls._opcvm_cache["Date"] = pd.to_datetime(cls._opcvm_cache["Date"])
                cls._opcvm_cache = cls._opcvm_cache.sort_values("Date")
            else:
                raise FileNotFoundError(f"Fichier OPCVM non trouvé: {OPCVM_FILE}")
        return cls._opcvm_cache.copy()

    @classmethod
    def load_volatility_data(cls) -> pd.DataFrame:
        """Charge les données de volatilité avec cache"""
        if cls._volatility_cache is None:
            if VOLATILITY_FILE.exists():
                cls._volatility_cache = pd.read_csv(VOLATILITY_FILE, parse_dates=["Date"])
                cls._volatility_cache["Date"] = pd.to_datetime(cls._volatility_cache["Date"])
                cls._volatility_cache = cls._volatility_cache.sort_values("Date")
            else:
                raise FileNotFoundError(f"Fichier volatilité non trouvé: {VOLATILITY_FILE}")
        return cls._volatility_cache.copy()

    @classmethod
    def load_final_dataset(cls) -> pd.DataFrame:
        """Charge le dataset final avec cache"""
        if cls._final_dataset_cache is None:
            if FINAL_DATASET_FILE.exists():
                cls._final_dataset_cache = pd.read_csv(FINAL_DATASET_FILE, parse_dates=["Date"])
                cls._final_dataset_cache["Date"] = pd.to_datetime(cls._final_dataset_cache["Date"])
                cls._final_dataset_cache = cls._final_dataset_cache.sort_values("Date")
            else:
                raise FileNotFoundError(f"Fichier final dataset non trouvé: {FINAL_DATASET_FILE}")
        return cls._final_dataset_cache.copy()

    @staticmethod
    def filter_by_period(df: pd.DataFrame, days: int) -> pd.DataFrame:
        """Filtre les données par nombre de jours"""
        if df.empty:
            return df
        latest_date = df["Date"].max()
        start_date = latest_date - timedelta(days=days)
        return df[df["Date"] >= start_date].copy()

    @staticmethod
    def get_masi_list(df: pd.DataFrame) -> List[MASIDataPoint]:
        """Convertit DataFrame MASI en liste de MASIDataPoint"""
        data_points = []
        for _, row in df.iterrows():
            data_points.append(
                MASIDataPoint(
                    date=row["Date"],
                    value=float(row.get("Valeur", row.get("Close", 0))),
                    variation=float(row.get("Variation %", None)) if "Variation %" in row else None,
                )
            )
        return data_points

    @staticmethod
    def get_opcvm_list(df: pd.DataFrame) -> List[OPCVMDataPoint]:
        """Convertit DataFrame OPCVM en liste de OPCVMDataPoint"""
        data_points = []
        for _, row in df.iterrows():
            data_points.append(
                OPCVMDataPoint(
                    date=row["Date"],
                    value=float(row.get("Valeur Liquidative", row.get("Value", 0))),
                    performance_1w=float(row.get("Performances glissantes 1 semaine", None)) if "Performances glissantes 1 semaine" in row else None,
                    performance_1m=float(row.get("Performances glissantes Depuis Début d'année", None)) if "Performances glissantes Depuis Début d'année" in row else None,
                    performance_6m=float(row.get("Performances glissantes 6 mois", None)) if "Performances glissantes 6 mois" in row else None,
                    performance_1y=float(row.get("Performances glissantes 1 an", None)) if "Performances glissantes 1 an" in row else None,
                )
            )
        return data_points

    @staticmethod
    def get_volatility_list(df: pd.DataFrame) -> List[VolatilityDataPoint]:
        """Convertit DataFrame de volatilité en liste de VolatilityDataPoint"""
        data_points = []
        for _, row in df.iterrows():
            data_points.append(
                VolatilityDataPoint(
                    date=row["Date"],
                    garch_vol=float(row.get("garch_vol", None)) if "garch_vol" in row else None,
                    vol_future_2w=float(row.get("vol_future_2w", None)) if "vol_future_2w" in row else None,
                    performances_1w=float(row.get("Performances glissantes 1 semaine", None)) if "Performances glissantes 1 semaine" in row else None,
                    variation=float(row.get("Variation %", None)) if "Variation %" in row else None,
                )
            )
        return data_points
