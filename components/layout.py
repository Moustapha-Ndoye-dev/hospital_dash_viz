"""
Layout principal — Assemblage de tous les composants.
Navbar + Sidebar + Page Container + Footer.
"""

import dash
from dash import html, dcc

from components.navbar import create_navbar
from components.sidebar import create_sidebar
from components.footer import create_footer


def create_main_layout() -> html.Div:
    """
    Crée le layout principal de l'application.

    Structure :
        ┌───────────────────────────────────┐
        │  NAVBAR                           │
        ├──────────┬────────────────────────┤
        │ SIDEBAR  │  dash.page_container   │
        │ (filtres)│  (contenu dynamique)   │
        ├──────────┴────────────────────────┤
        │  FOOTER                           │
        └───────────────────────────────────┘
    """
    # Spinner réutilisable : même aspect pour toute l’app (toutes pages + filtres)
    _loading_spinner = html.Div(
        className="loading-hud",
        children=[
            html.Div(
                className="loading-hud-inner",
                children=[
                    html.Div(
                        className="loading-hud-bar-wrap",
                        children=[html.Div(className="loading-hud-bar")],
                    ),
                    html.P(
                        "Chargement du tableau de bord…",
                        className="loading-hud-label",
                    ),
                ],
            ),
        ],
    )

    return html.Div(
        className="app-wrapper",
        children=[
            # Location pour navigation
            dcc.Location(id="url", refresh=False),

            # Navbar
            create_navbar(),

            # Corps : sidebar + toutes les pages sous un seul Loading (filtres inclus)
            html.Div(
                className="app-body",
                children=[
                    dcc.Loading(
                        id="page-loading",
                        type="circle",
                        color="#0AEFB7",
                        fullscreen=False,
                        delay_show=80,
                        delay_hide=80,
                        show_initially=False,
                        custom_spinner=_loading_spinner,
                        parent_className="page-loading-shell",
                        children=html.Div(
                            className="page-loading-zone",
                            children=[
                                # Store dans la zone chargée → interactions filtres / pages = même HUD
                                dcc.Store(id="filter-store", storage_type="session"),
                                create_sidebar(),
                                html.Main(
                                    className="main-content",
                                    children=[dash.page_container],
                                ),
                            ],
                        ),
                    ),
                ],
            ),

            # Footer
            create_footer(),
        ],
    )
