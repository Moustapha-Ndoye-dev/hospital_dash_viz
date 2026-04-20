"""
Callbacks — repli du panneau filtres (sidebar).
"""

from dash import Input, Output, State, callback, ctx, html


@callback(
    Output("sidebar-collapsed", "data"),
    Output("app-body", "className"),
    Output("btn-sidebar-toggle", "title"),
    Output("btn-sidebar-toggle", "children"),
    Input("btn-sidebar-toggle", "n_clicks"),
    State("sidebar-collapsed", "data"),
)
def toggle_sidebar(_n_clicks: int | None, collapsed):
    """Replie ou affiche la sidebar ; persistance via Store session."""
    collapsed = bool(collapsed) if collapsed is not None else False

    if ctx.triggered_id == "btn-sidebar-toggle":
        collapsed = not collapsed

    body_cls = "app-body app-body--sidebar-collapsed" if collapsed else "app-body"

    if collapsed:
        title = "Afficher le panneau filtres"
        children = [
            html.Span("▶", className="btn-sidebar-toggle-icon"),
            html.Span(" Filtres", className="btn-sidebar-toggle-text"),
        ]
    else:
        title = "Masquer le panneau filtres"
        children = [
            html.Span("◀", className="btn-sidebar-toggle-icon"),
            html.Span(" Filtres", className="btn-sidebar-toggle-text"),
        ]

    return collapsed, body_cls, title, children
