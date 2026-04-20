"""
Configuration globale — Dashboard Hospitalier
Master 2 CSDS · Projet Dashboard Hospitalier
"""

import os
from pathlib import Path

# ──────────────────────────────────────────────
# CHEMINS
# ──────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"
DATA_EXPORTS = BASE_DIR / "data" / "exports"
RAW_FILE = DATA_RAW / "hospital_data.csv"
CLEAN_FILE = DATA_PROCESSED / "hospital_clean.parquet"

# ──────────────────────────────────────────────
# PALETTE MÉDICALE (Dark Theme)
# ──────────────────────────────────────────────
COLORS = {
    "primary":        "#0D6E6E",
    "primary_light":  "#14919B",
    "accent":         "#0AEFB7",
    "success":        "#34D399",
    "warning":        "#FBBF24",
    "danger":         "#F87171",
    "info":           "#A78BFA",
    "bg_dark":        "#0A1018",
    "bg_body":        "#060A0F",
    "surface":        "#0F1720",
    "surface_light":  "#162232",
    "card":           "rgba(15, 23, 32, 0.82)",
    "card_border":    "rgba(255, 255, 255, 0.05)",
    "text":           "#E4ECF4",
    "text_secondary": "#7B8FA3",
    "text_muted":     "#3E5368",
}

# ──────────────────────────────────────────────
# COULEURS GRAPHIQUES  (7 nuances harmonieuses)
# ──────────────────────────────────────────────
CHART_PALETTE = [
    "#0AEFB7",  # Émeraude (accent)
    "#14919B",  # Teal
    "#FBBF24",  # Ambre
    "#F87171",  # Corail
    "#A78BFA",  # Lavande
    "#38BDF8",  # Ciel
    "#FB923C",  # Mandarine
]

# Couleurs spécifiques par département
DEPT_COLORS = {
    "Cardiologie":   "#F87171",
    "Dermatologie":  "#FB923C",
    "Gériatrie":     "#A78BFA",
    "Neurologie":    "#FBBF24",
    "Oncologie":     "#F472B6",
    "Orthopédie":    "#34D399",
    "Pneumologie":   "#38BDF8",
}

# Couleurs par maladie
MALADIE_COLORS = {
    "Alzheimer":     "#A78BFA",
    "Cancer":        "#F87171",
    "Eczéma":        "#FB923C",
    "Fracture":      "#34D399",
    "Hypertension":  "#FBBF24",
    "Infarctus":     "#F472B6",
    "Pneumonie":     "#38BDF8",
}

# Couleurs par traitement
TRAITEMENT_COLORS = {
    "Antibiotiques":   "#38BDF8",
    "Chirurgie":       "#F87171",
    "Médication":      "#FBBF24",
    "Physiothérapie":  "#34D399",
    "Radiothérapie":   "#A78BFA",
    "Soins spéciaux":  "#F472B6",
}

# ──────────────────────────────────────────────
# SEUILS & CATÉGORIES MÉDICALES
# ──────────────────────────────────────────────
TRANCHES_AGE = {
    "Pédiatrique (0-17)":   (0, 17),
    "Adulte (18-64)":       (18, 64),
    "Gériatrique (65+)":    (65, 200),
}

CATEGORIES_SEJOUR = {
    "Ambulatoire (1-2j)":  (1, 2),
    "Court (3-5j)":        (3, 5),
    "Moyen (6-10j)":       (6, 10),
    "Long (11-15j)":       (11, 15),
}

CLASSES_COUT = {
    "Faible (<2 000€)":       (0, 2000),
    "Modéré (2-4 000€)":      (2001, 4000),
    "Élevé (4-7 000€)":       (4001, 7000),
    "Critique (>7 000€)":     (7001, float("inf")),
}

SAISONS = {
    12: "Hiver", 1: "Hiver", 2: "Hiver",
    3: "Printemps", 4: "Printemps", 5: "Printemps",
    6: "Été", 7: "Été", 8: "Été",
    9: "Automne", 10: "Automne", 11: "Automne",
}

JOURS_SEMAINE = {
    0: "Lundi", 1: "Mardi", 2: "Mercredi",
    3: "Jeudi", 4: "Vendredi", 5: "Samedi", 6: "Dimanche",
}

MOIS_NOMS = {
    1: "Jan", 2: "Fév", 3: "Mar", 4: "Avr",
    5: "Mai", 6: "Juin", 7: "Juil", 8: "Août",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Déc",
}

# ──────────────────────────────────────────────
# TEMPLATE PLOTLY (appliqué à tous les graphiques)
# ──────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Outfit, DM Sans, sans-serif", color="#E4ECF4", size=11),
    margin=dict(l=50, r=20, t=50, b=40),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.035)",
        zerolinecolor="rgba(255,255,255,0.05)",
        title_font=dict(size=10, color="#7B8FA3", family="Outfit, sans-serif"),
        tickfont=dict(size=9.5, color="#7B8FA3", family="DM Sans, sans-serif"),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.035)",
        zerolinecolor="rgba(255,255,255,0.05)",
        title_font=dict(size=10, color="#7B8FA3", family="Outfit, sans-serif"),
        tickfont=dict(size=9.5, color="#7B8FA3", family="DM Sans, sans-serif"),
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(size=10, color="#7B8FA3", family="DM Sans, sans-serif"),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
    hoverlabel=dict(
        bgcolor="#162232",
        bordercolor="rgba(10, 239, 183, 0.2)",
        font=dict(size=11, color="#E4ECF4", family="DM Sans, sans-serif"),
    ),
    title=dict(
        font=dict(size=13, color="#E4ECF4", family="Outfit, sans-serif"),
        x=0,
        xanchor="left",
    ),
)

# ──────────────────────────────────────────────
# APPLICATION
# ──────────────────────────────────────────────
APP_TITLE = "Dashboard Hospitalier"
APP_SUBTITLE = "Dakar — Analyse & Aide à la Décision"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Moustapha Ndoye"
APP_YEAR = "2025"

DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
PORT = int(os.environ.get("PORT", 8050))

# Par défaut : pas de reloader Flask (sinon 2 processus = double import pandas/plotly + double lecture données).
# Pour le rechargement auto du code : DASH_USE_RELOADER=true
DASH_USE_RELOADER = os.environ.get("DASH_USE_RELOADER", "false").lower() == "true"

# DevTools Dash : la validation des props ralentit fortement les callbacks au premier rendu.
DASH_DEV_TOOLS_PROPS_CHECK = os.environ.get("DASH_DEV_TOOLS_PROPS_CHECK", "false").lower() == "true"
