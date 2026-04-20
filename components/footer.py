"""
Footer — Pied de page avec crédits et métadonnées.
"""

from dash import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import APP_VERSION, APP_AUTHOR, APP_YEAR


def create_footer() -> html.Footer:
    """Crée le pied de page du dashboard."""
    return html.Footer(
        className="footer",
        children=[
            html.Div(
                className="footer-content",
                children=[
                    html.Span(
                        f"🏥 Dashboard Hospitalier v{APP_VERSION}",
                        className="footer-brand",
                    ),
                    html.Span("•", className="footer-dot"),
                    html.Span(
                        f"Dakar — {APP_AUTHOR}",
                        className="footer-credits",
                    ),
                    html.Span("•", className="footer-dot"),
                    html.Span(
                        "Données à usage académique",
                        className="footer-disclaimer",
                    ),
                ],
            ),
        ],
    )
