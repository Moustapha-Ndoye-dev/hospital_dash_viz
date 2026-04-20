"""
Entrées filtres partagées — même source que la sidebar pour éviter toute désynchronisation
avec dcc.Store (session) au chargement.
"""

from dash import Input, State


FILTER_INPUTS = (
    Input("filter-dept", "value"),
    Input("filter-maladie", "value"),
    Input("filter-sexe", "value"),
    Input("filter-age", "value"),
    Input("filter-traitement", "value"),
    Input("filter-dates", "start_date"),
    Input("filter-dates", "end_date"),
)

FILTER_STATES = (
    State("filter-dept", "value"),
    State("filter-maladie", "value"),
    State("filter-sexe", "value"),
    State("filter-age", "value"),
    State("filter-traitement", "value"),
    State("filter-dates", "start_date"),
    State("filter-dates", "end_date"),
)


def build_filters_dict(dept, maladie, sexe, age, traitement, date_start, date_end):
    """Construit le dict attendu par utils.data_loader.apply_filters."""
    return {
        "departement": dept or [],
        "maladie": maladie or [],
        "sexe": sexe or "Tous",
        "tranche_age": age or [],
        "traitement": traitement or [],
        "date_start": date_start,
        "date_end": date_end,
    }
