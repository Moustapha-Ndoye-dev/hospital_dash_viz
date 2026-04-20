"""
Module de calculs statistiques hospitaliers.
Fournit les KPIs métier et indicateurs de performance.
"""

import pandas as pd
import numpy as np


def compute_kpis(df: pd.DataFrame) -> dict:
    """
    Calcule les KPIs globaux du tableau de bord.

    Indicateurs hospitaliers standards :
        - Nombre total de patients
        - Coût total et moyen
        - DMS (Durée Moyenne de Séjour)
        - Coût moyen par journée d'hospitalisation
        - Taux de séjour long (>10 jours)
        - Indice de gravité moyen

    Returns:
        dict : KPIs formatés
    """
    if len(df) == 0:
        return {
            "total_patients": 0,
            "cout_total": 0,
            "cout_moyen": 0,
            "dms": 0,
            "cout_par_jour": 0,
            "taux_sejour_long": 0,
            "gravite_moyenne": 0,
            "age_moyen": 0,
            "ratio_hommes": 0,
            "patients_critiques": 0,
        }

    return {
        "total_patients": len(df),
        "cout_total": int(df["Cout"].sum()),
        "cout_moyen": round(df["Cout"].mean(), 0),
        "dms": round(df["DureeSejour"].mean(), 1),
        "cout_par_jour": round(
            df["Cout"].sum() / df["DureeSejour"].sum(), 0
        ),
        "taux_sejour_long": round(
            (df["DureeSejour"] > 10).sum() / len(df) * 100, 1
        ),
        "gravite_moyenne": round(df["IndiceGravite"].mean(), 3),
        "age_moyen": round(df["Age"].mean(), 1),
        "ratio_hommes": round(
            (df["Sexe"] == "M").sum() / len(df) * 100, 1
        ),
        "patients_critiques": int(
            (df["ClasseCout"] == "Critique (>7 000€)").sum()
        ),
    }


def stats_par_departement(df: pd.DataFrame) -> pd.DataFrame:
    """
    Statistiques agrégées par département hospitalier.

    Métriques :
        - Volume de patients
        - Coût total et moyen
        - DMS
        - Coût par jour
        - Taux de séjour long
        - Âge moyen
    """
    if len(df) == 0:
        return pd.DataFrame()

    stats = df.groupby("Departement").agg(
        Patients=("PatientID", "count"),
        CoutTotal=("Cout", "sum"),
        CoutMoyen=("Cout", "mean"),
        CoutMedian=("Cout", "median"),
        DMS=("DureeSejour", "mean"),
        CoutParJour=("CoutParJour", "mean"),
        AgeMoyen=("Age", "mean"),
        GraviteMoyenne=("IndiceGravite", "mean"),
    ).round(1)

    stats["TauxSejourLong"] = df.groupby("Departement").apply(
        lambda x: round((x["DureeSejour"] > 10).sum() / len(x) * 100, 1)
    )

    stats = stats.sort_values("CoutTotal", ascending=False)
    return stats.reset_index()


def stats_par_maladie(df: pd.DataFrame) -> pd.DataFrame:
    """Statistics agrégées par pathologie."""
    if len(df) == 0:
        return pd.DataFrame()

    stats = df.groupby("Maladie").agg(
        Patients=("PatientID", "count"),
        CoutTotal=("Cout", "sum"),
        CoutMoyen=("Cout", "mean"),
        DMS=("DureeSejour", "mean"),
        CoutParJour=("CoutParJour", "mean"),
        AgeMoyen=("Age", "mean"),
        GraviteMoyenne=("IndiceGravite", "mean"),
    ).round(1)

    stats["Prevalence"] = (stats["Patients"] / stats["Patients"].sum() * 100).round(1)
    stats = stats.sort_values("CoutTotal", ascending=False)
    return stats.reset_index()


def stats_par_traitement(df: pd.DataFrame) -> pd.DataFrame:
    """Statistiques agrégées par type de traitement."""
    if len(df) == 0:
        return pd.DataFrame()

    stats = df.groupby("Traitement").agg(
        Patients=("PatientID", "count"),
        CoutMoyen=("Cout", "mean"),
        DMS=("DureeSejour", "mean"),
        CoutParJour=("CoutParJour", "mean"),
    ).round(1)

    stats = stats.sort_values("CoutMoyen", ascending=False)
    return stats.reset_index()


def tendance_mensuelle(df: pd.DataFrame) -> pd.DataFrame:
    """Tendance des admissions et coûts par mois."""
    if len(df) == 0:
        return pd.DataFrame()

    monthly = df.groupby("AnneeMois").agg(
        Admissions=("PatientID", "count"),
        CoutTotal=("Cout", "sum"),
        CoutMoyen=("Cout", "mean"),
        DMS=("DureeSejour", "mean"),
    ).round(1)

    monthly["CoutCumule"] = monthly["CoutTotal"].cumsum()
    return monthly.reset_index()


def matrice_maladie_departement(df: pd.DataFrame,
                                  valeur: str = "count") -> pd.DataFrame:
    """
    Matrice croisée maladie × département.

    Args:
        valeur: 'count' pour le nombre de cas, 'mean_cost' pour le coût moyen
    """
    if len(df) == 0:
        return pd.DataFrame()

    if valeur == "count":
        return pd.crosstab(df["Maladie"], df["Departement"])
    elif valeur == "mean_cost":
        return df.pivot_table(
            values="Cout", index="Maladie", columns="Departement",
            aggfunc="mean"
        ).round(0)
    return pd.DataFrame()


def top_sejours_couteux(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Retourne les N séjours les plus coûteux."""
    cols = ["PatientID", "Age", "Sexe", "Departement", "Maladie",
            "DureeSejour", "Cout", "Traitement", "CoutParJour"]
    return df.nlargest(n, "Cout")[cols].reset_index(drop=True)


def distribution_stats(series: pd.Series) -> dict:
    """Statistiques descriptives complètes pour une série numérique."""
    return {
        "n": len(series),
        "mean": round(series.mean(), 2),
        "median": round(series.median(), 2),
        "std": round(series.std(), 2),
        "min": round(series.min(), 2),
        "max": round(series.max(), 2),
        "q1": round(series.quantile(0.25), 2),
        "q3": round(series.quantile(0.75), 2),
        "iqr": round(series.quantile(0.75) - series.quantile(0.25), 2),
        "skew": round(series.skew(), 2),
        "kurtosis": round(series.kurtosis(), 2),
    }
