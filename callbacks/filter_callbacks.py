"""
Callbacks des filtres globaux.
Met à jour le dcc.Store partagé entre toutes les pages.
"""

from dash import callback, Input, Output, State
from utils.data_loader import load_data, apply_filters, get_filter_options
from utils.filter_inputs import FILTER_INPUTS, build_filters_dict


@callback(
    Output("filter-store", "data"),
    Output("filter-count", "children"),
    *FILTER_INPUTS,
)
def update_filter_store(dept, maladie, sexe, age, traitement,
                        date_start, date_end):
    """
    Centralise les valeurs de filtre dans un Store partagé.
    Met à jour le compteur de résultats dans la sidebar.
    """
    filters = build_filters_dict(
        dept, maladie, sexe, age, traitement, date_start, date_end
    )

    # Compter les résultats filtrés
    df = load_data()
    df_filtered = apply_filters(df, filters)
    count = len(df_filtered)
    total = len(df)
    pct = round(count / total * 100, 0) if total > 0 else 0

    count_text = f"{count} / {total} patients ({pct:.0f}%)"

    return filters, count_text


@callback(
    Output("filter-dept", "value"),
    Output("filter-maladie", "value"),
    Output("filter-sexe", "value"),
    Output("filter-age", "value"),
    Output("filter-traitement", "value"),
    Output("filter-dates", "start_date"),
    Output("filter-dates", "end_date"),
    Input("btn-reset-filters", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(n_clicks):
    """Réinitialise tous les filtres à leurs valeurs par défaut."""
    df = load_data()
    options = get_filter_options(df)
    return (
        [],              # dept
        [],              # maladie
        "Tous",          # sexe
        [],              # age
        [],              # traitement
        options["date_min"],  # date start
        options["date_max"],  # date end
    )
