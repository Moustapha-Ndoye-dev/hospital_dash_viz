"""
Pipeline de nettoyage des données hospitalières.
Vérifie les types, convertit les dates, normalise l'encodage.
"""

import pandas as pd
from pathlib import Path


def clean_data(filepath: Path) -> pd.DataFrame:
    """
    Charge et nettoie le fichier CSV brut.

    Étapes :
        1. Lecture avec séparateur point-virgule et encodage UTF-8
        2. Suppression des doublons éventuels
        3. Conversion des colonnes date au format datetime
        4. Vérification et cast des types numériques
        5. Normalisation des chaînes de caractères (strip, title-case)
        6. Validation de la cohérence DureeSejour vs dates

    Returns:
        pd.DataFrame : données nettoyées
    """
    # --- Lecture brute ---
    df = pd.read_csv(filepath, sep=";", encoding="utf-8")

    # --- Doublons ---
    n_before = len(df)
    df = df.drop_duplicates(subset=["PatientID"], keep="first")
    n_dupes = n_before - len(df)
    if n_dupes > 0:
        print(f"[CLEAN] {n_dupes} doublons supprimés.")

    # --- Conversion des dates (format DD/MM/YYYY) ---
    df["DateAdmission"] = pd.to_datetime(
        df["DateAdmission"], format="%d/%m/%Y", errors="coerce"
    )
    df["DateSortie"] = pd.to_datetime(
        df["DateSortie"], format="%d/%m/%Y", errors="coerce"
    )

    # Supprimer les lignes avec des dates invalides
    n_bad_dates = df[["DateAdmission", "DateSortie"]].isna().any(axis=1).sum()
    if n_bad_dates > 0:
        print(f"[CLEAN] {n_bad_dates} lignes avec dates invalides supprimées.")
        df = df.dropna(subset=["DateAdmission", "DateSortie"])

    # --- Types numériques ---
    df["PatientID"] = df["PatientID"].astype(int)
    df["Age"] = df["Age"].astype(int)
    df["DureeSejour"] = df["DureeSejour"].astype(int)
    df["Cout"] = df["Cout"].astype(float)

    # --- Normalisation des chaînes ---
    str_cols = ["Sexe", "Departement", "Maladie", "Traitement"]
    for col in str_cols:
        df[col] = df[col].str.strip()

    # --- Validation cohérence durée vs dates ---
    duree_calc = (df["DateSortie"] - df["DateAdmission"]).dt.days
    incoherent = (duree_calc != df["DureeSejour"]).sum()
    if incoherent > 0:
        print(f"[CLEAN] {incoherent} incohérences durée/dates (corrigé par dates).")
        df["DureeSejour"] = duree_calc.clip(lower=1)

    # --- Valeurs aberrantes ---
    df["Age"] = df["Age"].clip(lower=0, upper=120)
    df["Cout"] = df["Cout"].clip(lower=0)
    df["DureeSejour"] = df["DureeSejour"].clip(lower=1)

    # --- Reset index ---
    df = df.reset_index(drop=True)

    print(f"[CLEAN] Pipeline terminé : {len(df)} patients, {df.shape[1]} colonnes.")
    return df
