"""
Point d'entrée principal — Dashboard Hospitalier
Master 2 CSDS · Application Dash Multi-Pages
"""

import dash
from dash import Dash
from components.layout import create_main_layout

# ──────────────────────────────────────────────
# INITIALISATION
# ──────────────────────────────────────────────
app = Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    suppress_callback_exceptions=True,
    title="Dashboard Hospitalier",
    update_title="Chargement...",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        {"name": "description", "content": "Dashboard d'analyse hospitalière — Master 2 CSDS"},
        {"charset": "UTF-8"},
    ],
)

# Serveur Flask sous-jacent (pour Gunicorn)
server = app.server

# Layout principal
app.layout = create_main_layout()

# ──────────────────────────────────────────────
# IMPORT DES CALLBACKS PARTAGÉS
# (les callbacks de pages sont auto-enregistrés
#  par Dash Pages depuis les fichiers pages/)
# ──────────────────────────────────────────────
import callbacks.filter_callbacks  # noqa: F401, E402
import callbacks.sidebar_callbacks  # noqa: F401, E402

# ──────────────────────────────────────────────
# LANCEMENT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    from config import DEBUG, PORT, DASH_USE_RELOADER, DASH_DEV_TOOLS_PROPS_CHECK

    app.run(
        debug=DEBUG,
        port=PORT,
        use_reloader=DASH_USE_RELOADER,
        dev_tools_props_check=DASH_DEV_TOOLS_PROPS_CHECK,
    )
