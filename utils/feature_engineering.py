"""
Feature Engineering — Variables dérivées pour l'analyse hospitalière.
Crée des indicateurs métier pertinents pour la prise de décision.
"""

import pandas as pd
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import TRANCHES_AGE, CATEGORIES_SEJOUR, CLASSES_COUT, SAISONS, JOURS_SEMAINE, MOIS_NOMS


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrichit le DataFrame avec des variables dérivées métier.

    Variables créées :
        - CoutParJour         : efficience financière (€/jour)
        - TrancheAge          : catégorie démographique
        - CategorieSejour     : classification durée séjour
        - ClasseCout          : segmentation financière
        - MoisAdmission       : numéro du mois (1-12)
        - NomMois             : nom abrégé du mois
        - AnneeMois           : format YYYY-MM pour séries temporelles
        - JourSemaine         : jour de la semaine (0=Lundi)
        - NomJour             : nom du jour
        - Saison              : saison climatique
        - SemaineAnnee        : numéro de semaine ISO
        - DureeReelle         : durée calculée à partir des dates (jours)
        - IndiceGravite       : score composite (coût × durée normalisés)
        - CoutNorme           : coût normalisé [0-1]
        - DureeNorme          : durée normalisée [0-1]

    Returns:
        pd.DataFrame : données enrichies
    """
    df = df.copy()

    # ── Coût par journée d'hospitalisation (€/jour) ──
    df["CoutParJour"] = (df["Cout"] / df["DureeSejour"]).round(2)

    # ── Tranche d'âge (catégories médicales standard) ──
    df["TrancheAge"] = pd.cut(
        df["Age"],
        bins=[0, 17, 64, 200],
        labels=["Pédiatrique (0-17)", "Adulte (18-64)", "Gériatrique (65+)"],
        include_lowest=True,
    ).astype(str)

    # ── Catégorie de séjour ──
    df["CategorieSejour"] = pd.cut(
        df["DureeSejour"],
        bins=[0, 2, 5, 10, 15],
        labels=["Ambulatoire (1-2j)", "Court (3-5j)", "Moyen (6-10j)", "Long (11-15j)"],
        include_lowest=True,
    ).astype(str)

    # ── Classe de coût ──
    df["ClasseCout"] = pd.cut(
        df["Cout"],
        bins=[0, 2000, 4000, 7000, float("inf")],
        labels=["Faible (<2 000€)", "Modéré (2-4 000€)", "Élevé (4-7 000€)", "Critique (>7 000€)"],
        include_lowest=True,
    ).astype(str)

    # ── Variables temporelles ──
    df["MoisAdmission"] = df["DateAdmission"].dt.month
    df["NomMois"] = df["MoisAdmission"].map(MOIS_NOMS)
    df["AnneeMois"] = df["DateAdmission"].dt.to_period("M").astype(str)
    df["JourSemaine"] = df["DateAdmission"].dt.dayofweek
    df["NomJour"] = df["JourSemaine"].map(JOURS_SEMAINE)
    df["Saison"] = df["MoisAdmission"].map(SAISONS)
    df["SemaineAnnee"] = df["DateAdmission"].dt.isocalendar().week.astype(int)
    df["AnneeAdmission"] = df["DateAdmission"].dt.year

    # ── Durée réelle depuis les dates ──
    df["DureeReelle"] = (df["DateSortie"] - df["DateAdmission"]).dt.days

    # ── Score de gravité composite ──
    # Normalisation min-max du coût et de la durée
    cout_min, cout_max = df["Cout"].min(), df["Cout"].max()
    dur_min, dur_max = df["DureeSejour"].min(), df["DureeSejour"].max()

    df["CoutNorme"] = ((df["Cout"] - cout_min) / (cout_max - cout_min)).round(4)
    df["DureeNorme"] = ((df["DureeSejour"] - dur_min) / (dur_max - dur_min)).round(4)

    # Indice de gravité = moyenne pondérée (60% coût, 40% durée)
    df["IndiceGravite"] = (0.6 * df["CoutNorme"] + 0.4 * df["DureeNorme"]).round(4)

    print(f"[FEATURES] {len(df.columns) - 10} variables dérivées créées ({len(df.columns)} colonnes total).")
    return df
