"""
Barre de navigation — Navigation principale du dashboard.
"""

from dash import html, dcc


def create_navbar() -> html.Div:
    """
    Crée la barre de navigation supérieure.

    Contient :
        - Logo texte + icône hôpital
        - Liens vers toutes les pages
        - Indicateur de page active (géré par CSS)
    """
    nav_links = [
        {"label": "Accueil",       "href": "/",              "icon": "📊"},
        {"label": "Patients",      "href": "/patients",      "icon": "👥"},
        {"label": "Pathologies",   "href": "/pathologies",   "icon": "🩺"},
        {"label": "Finances",      "href": "/finances",      "icon": "💰"},
        {"label": "Séjours",       "href": "/sejours",       "icon": "🏨"},
        {"label": "Rapport",       "href": "/rapport",       "icon": "📄"},
    ]

    return html.Nav(
        className="navbar",
        children=[
            html.Div(
                className="navbar-start",
                children=[
                    html.Div(
                        className="navbar-brand",
                        children=[
                            html.Span("🏥", className="navbar-logo-icon"),
                            html.Div([
                                html.Span("Dashboard", className="navbar-brand-primary"),
                                html.Span("Hospitalier", className="navbar-brand-secondary"),
                            ], className="navbar-brand-text"),
                        ],
                    ),
                    html.Button(
                        id="btn-sidebar-toggle",
                        className="btn-sidebar-toggle",
                        type="button",
                        title="Masquer le panneau filtres",
                        n_clicks=0,
                        children=[
                            html.Span("◀", className="btn-sidebar-toggle-icon"),
                            html.Span(" Filtres", className="btn-sidebar-toggle-text"),
                        ],
                    ),
                ],
            ),
            # Liens de navigation
            html.Div(
                className="navbar-links",
                children=[
                    dcc.Link(
                        className="navbar-link",
                        href=link["href"],
                        children=[
                            html.Span(link["icon"], className="nav-icon"),
                            html.Span(link["label"], className="nav-label"),
                        ],
                    )
                    for link in nav_links
                ],
            ),
            # Badge version
            html.Div(
                className="navbar-badge",
                children=[
                    html.Span("v1.0", className="version-badge"),
                ],
            ),
        ],
    )
