"""
Chargeur de données centralisé avec cache mémoire.
Point d'accès unique pour toutes les pages et callbacks.
"""

import os
import sys
from functools import lru_cache
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import RAW_FILE, CLEAN_FILE
from utils.cleaning import clean_data
from utils.feature_engineering import engineer_features


def _loader_log(msg: str) -> None:
    if os.environ.get("DASH_QUIET_LOADER", "false").lower() != "true":
        print(f"[LOADER] {msg}")


@lru_cache(maxsize=1)
def load_data() -> pd.DataFrame:
    """
    Charge les données nettoyées et enrichies.
    Si le fichier processed n'existe pas, exécute le pipeline complet.
    Résultat mis en cache pour performance optimale.

    Returns:
        pd.DataFrame : données prêtes à l'analyse
    """
    if CLEAN_FILE.exists():
        try:
            df = pd.read_parquet(CLEAN_FILE, engine="pyarrow")
        except Exception:
            df = pd.read_parquet(CLEAN_FILE)
        _loader_log(f"Données chargées (Parquet) : {len(df)} séjours.")
    else:
        _loader_log("Première exécution — pipeline de nettoyage…")
        df = clean_data(RAW_FILE)
        df = engineer_features(df)

        # Sauvegarde du fichier nettoyé au format Parquet (plus performant)
        CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(CLEAN_FILE, index=False)
        _loader_log(f"Pipeline terminé — fichier : {CLEAN_FILE}")

    return df


def _admission_datetimes(df: pd.DataFrame) -> pd.Series:
    """Dates d'admission en datetime naïf (comparaisons stables prod / fuseaux)."""
    s = pd.to_datetime(df["DateAdmission"])
    if getattr(s.dtype, "tz", None) is not None:
        s = s.dt.tz_convert("UTC").dt.tz_localize(None)
    return s


def apply_filters(df: pd.DataFrame, filters: dict | None) -> pd.DataFrame:
    """
    Applique les filtres sélectionnés par l'utilisateur.

    Args:
        df: DataFrame source
        filters: dictionnaire des valeurs de filtre depuis dcc.Store
            - departement : list[str] ou None
            - maladie : list[str] ou None
            - sexe : str ('M', 'F', 'Tous') ou None
            - tranche_age : list[str] ou None
            - traitement : list[str] ou None
            - date_start : str (YYYY-MM-DD) ou None
            - date_end : str (YYYY-MM-DD) ou None

    Returns:
        pd.DataFrame filtré
    """
    if filters is None:
        return df
    if not filters:
        return df

    mask = pd.Series(True, index=df.index)

    # Filtre département
    dept = filters.get("departement")
    if dept and len(dept) > 0:
        mask &= df["Departement"].isin(dept)

    # Filtre maladie
    maladie = filters.get("maladie")
    if maladie and len(maladie) > 0:
        mask &= df["Maladie"].isin(maladie)

    # Filtre sexe
    sexe = filters.get("sexe")
    if sexe and sexe != "Tous":
        mask &= df["Sexe"] == sexe

    # Filtre tranche d'âge
    tranche = filters.get("tranche_age")
    if tranche and len(tranche) > 0:
        mask &= df["TrancheAge"].isin(tranche)

    # Filtre traitement
    traitement = filters.get("traitement")
    if traitement and len(traitement) > 0:
        mask &= df["Traitement"].isin(traitement)

    # Filtre dates : intersection [utilisateur] ∩ [min/max données]. Si la session garde une
    # ancienne plage hors jeu de données (redéploiement), on retombe sur la plage utile du fichier.
    adm = _admission_datetimes(df)
    adm_day = adm.dt.normalize()
    data_min = adm_day.min()
    data_max = adm_day.max()

    date_start = filters.get("date_start")
    date_end = filters.get("date_end")
    if date_start or date_end:
        ds = (
            pd.to_datetime(date_start).normalize()
            if date_start
            else data_min
        )
        de = (
            pd.to_datetime(date_end).normalize()
            if date_end
            else data_max
        )
        ds = max(ds, data_min)
        de = min(de, data_max)
        if ds > de:
            ds, de = data_min, data_max
        mask &= adm_day >= ds
        mask &= adm_day <= de

    return df[mask].copy()


def get_filter_options(df: pd.DataFrame) -> dict:
    """
    Retourne les options disponibles pour chaque filtre.

    Returns:
        dict avec les listes d'options pour chaque filtre
    """
    return {
        "departements": sorted(df["Departement"].unique().tolist()),
        "maladies": sorted(df["Maladie"].unique().tolist()),
        "traitements": sorted(df["Traitement"].unique().tolist()),
        "tranches_age": sorted(df["TrancheAge"].unique().tolist()),
        "date_min": df["DateAdmission"].min().strftime("%Y-%m-%d"),
        "date_max": df["DateAdmission"].max().strftime("%Y-%m-%d"),
    }
