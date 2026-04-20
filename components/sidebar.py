"""
Sidebar — Panneau de filtres globaux.
Persiste entre les pages via dcc.Store.
"""

from dash import html, dcc
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_loader import load_data, get_filter_options


def create_sidebar() -> html.Aside:
    """
    Crée le panneau latéral avec tous les filtres interactifs.

    Filtres :
        - Département (multi-select)
        - Maladie (multi-select)
        - Sexe (radio)
        - Tranche d'âge (checklist)
        - Traitement (multi-select)
        - Période (date range)
        - Bouton réinitialiser
    """
    df = load_data()
    options = get_filter_options(df)

    return html.Aside(
        className="sidebar",
        children=[
            # Titre
            html.Div(
                className="sidebar-header",
                children=[
                    html.Span("⚙️", className="sidebar-icon"),
                    html.H3("Filtres", className="sidebar-title"),
                ],
            ),

            html.Hr(className="sidebar-divider"),

            # --- Département ---
            html.Div(className="filter-group", children=[
                html.Label("Département", className="filter-label"),
                dcc.Dropdown(
                    id="filter-dept",
                    options=[{"label": d, "value": d} for d in options["departements"]],
                    value=[],
                    multi=True,
                    placeholder="Tous les départements",
                    className="filter-dropdown",
                    clearable=True,
                ),
            ]),

            # --- Maladie ---
            html.Div(className="filter-group", children=[
                html.Label("Pathologie", className="filter-label"),
                dcc.Dropdown(
                    id="filter-maladie",
                    options=[{"label": m, "value": m} for m in options["maladies"]],
                    value=[],
                    multi=True,
                    placeholder="Toutes les pathologies",
                    className="filter-dropdown",
                    clearable=True,
                ),
            ]),

            # --- Sexe ---
            html.Div(className="filter-group", children=[
                html.Label("Sexe", className="filter-label"),
                dcc.RadioItems(
                    id="filter-sexe",
                    options=[
                        {"label": " Tous", "value": "Tous"},
                        {"label": " Homme", "value": "M"},
                        {"label": " Femme", "value": "F"},
                    ],
                    value="Tous",
                    className="filter-radio",
                    inline=True,
                ),
            ]),

            # --- Tranche d'âge ---
            html.Div(className="filter-group", children=[
                html.Label("Tranche d'âge", className="filter-label"),
                dcc.Checklist(
                    id="filter-age",
                    options=[{"label": f" {t}", "value": t} for t in options["tranches_age"]],
                    value=[],
                    className="filter-checklist",
                ),
            ]),

            # --- Traitement ---
            html.Div(className="filter-group", children=[
                html.Label("Traitement", className="filter-label"),
                dcc.Dropdown(
                    id="filter-traitement",
                    options=[{"label": t, "value": t} for t in options["traitements"]],
                    value=[],
                    multi=True,
                    placeholder="Tous les traitements",
                    className="filter-dropdown",
                    clearable=True,
                ),
            ]),

            # --- Période ---
            html.Div(className="filter-group", children=[
                html.Label("Période d'admission", className="filter-label"),
                dcc.DatePickerRange(
                    id="filter-dates",
                    start_date=options["date_min"],
                    end_date=options["date_max"],
                    min_date_allowed=options["date_min"],
                    max_date_allowed=options["date_max"],
                    display_format="DD/MM/YYYY",
                    className="filter-datepicker",
                ),
            ]),

            html.Hr(className="sidebar-divider"),

            # --- Bouton réinitialiser ---
            html.Button(
                id="btn-reset-filters",
                className="btn-reset",
                children=[
                    html.Span("↺", style={"marginRight": "6px"}),
                    "Réinitialiser",
                ],
            ),

            # --- Compteur résultats ---
            html.Div(
                id="filter-count",
                className="filter-count",
                children="500 patients",
            ),
        ],
    )
