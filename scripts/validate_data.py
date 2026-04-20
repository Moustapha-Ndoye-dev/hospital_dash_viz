#!/usr/bin/env python3
"""
Validation des données hospitalières (schéma, cohérence minimale).
À lancer en CI ou avant déploiement : exit 0 si OK, 1 sinon.

Usage :
    python scripts/validate_data.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Colonnes attendues après nettoyage + feature engineering (load_data)
REQUIRED_COLUMNS = [
    "PatientID",
    "Age",
    "Sexe",
    "Departement",
    "Maladie",
    "DureeSejour",
    "Cout",
    "DateAdmission",
    "DateSortie",
    "Traitement",
    "CoutParJour",
    "TrancheAge",
    "CategorieSejour",
    "ClasseCout",
    "MoisAdmission",
    "NomMois",
    "AnneeMois",
    "JourSemaine",
    "NomJour",
    "Saison",
    "SemaineAnnee",
    "AnneeAdmission",
    "DureeReelle",
    "CoutNorme",
    "DureeNorme",
    "IndiceGravite",
]


def main() -> int:
    os.chdir(ROOT)
    from config import RAW_FILE

    if not RAW_FILE.is_file():
        print(f"[ERREUR] Fichier brut introuvable : {RAW_FILE}")
        print("         Vérifie que data/raw/hospital_data.csv est versionné et poussé sur Git.")
        return 1

    # Charge via le pipeline officiel (crée le Parquet si absent)
    from utils.data_loader import load_data

    df = load_data()

    if df is None or len(df) == 0:
        print("[ERREUR] DataFrame vide après chargement.")
        return 1

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        print(f"[ERREUR] Colonnes manquantes : {missing}")
        return 1

    # Contrôles métier légers
    null_dates = df["DateAdmission"].isna().sum() + df["DateSortie"].isna().sum()
    if null_dates > 0:
        print(f"[ERREUR] Dates manquantes : {null_dates}")
        return 1

    if (df["Cout"] < 0).any():
        print("[ERREUR] Coûts négatifs détectés.")
        return 1

    if (df["DureeSejour"] < 1).any():
        print("[ERREUR] Durée de séjour < 1 jour.")
        return 1

    sexe_ok = df["Sexe"].isin(["M", "F"]).all()
    if not sexe_ok:
        print("[ERREUR] Valeurs inattendues dans Sexe (attendu M/F).")
        return 1

    print(f"[OK] Données valides : {len(df)} séjours, {len(df.columns)} colonnes.")
    print(
        f"[OK] Periode admissions : {df['DateAdmission'].min().date()} -> "
        f"{df['DateAdmission'].max().date()}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
