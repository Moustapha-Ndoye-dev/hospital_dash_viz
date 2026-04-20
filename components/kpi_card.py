"""
Composant KPI Card — Carte indicateur réutilisable.
Design glassmorphism avec icône, valeur et variation.
"""

from dash import html


def kpi_card(title: str, value: str, icon: str,
             color: str = "#00B4D8", subtitle: str = "",
             card_id: str = "") -> html.Div:
    """
    Crée une carte KPI professionnelle.

    Args:
        title: libellé de l'indicateur
        value: valeur formatée
        icon: emoji ou icône
        color: couleur d'accent (bordure gauche)
        subtitle: texte secondaire (ex: variation)
        card_id: identifiant HTML optionnel

    Returns:
        html.Div : composant carte KPI
    """
    children = [
        html.Div(
            className="kpi-card-header",
            children=[
                html.Span(icon, className="kpi-icon"),
                html.Span(title, className="kpi-title"),
            ],
        ),
        html.Div(
            className="kpi-value",
            children=value,
            style={"color": color},
        ),
    ]
    if subtitle:
        children.append(html.Div(className="kpi-subtitle", children=subtitle))

    props = {
        "className": "kpi-card",
        "style": {"borderLeft": f"4px solid {color}"},
        "children": children,
    }
    if card_id:
        props["id"] = card_id

    return html.Div(**props)


def kpi_mini(label: str, value: str, color: str = "#8A95A9") -> html.Div:
    """Mini carte KPI pour les sections secondaires."""
    return html.Div(
        className="kpi-mini",
        children=[
            html.Span(value, className="kpi-mini-value", style={"color": color}),
            html.Span(label, className="kpi-mini-label"),
        ],
    )


def stat_row(label: str, value: str, bar_pct: float = 0,
             color: str = "#00B4D8") -> html.Div:
    """
    Ligne de statistique avec barre de progression horizontale.
    Utilisée dans les classements et tops.
    """
    return html.Div(
        className="stat-row",
        children=[
            html.Div(
                className="stat-row-info",
                children=[
                    html.Span(label, className="stat-row-label"),
                    html.Span(value, className="stat-row-value"),
                ],
            ),
            html.Div(
                className="stat-row-bar-bg",
                children=[
                    html.Div(
                        className="stat-row-bar",
                        style={
                            "width": f"{min(bar_pct, 100)}%",
                            "backgroundColor": color,
                        },
                    )
                ],
            ),
        ],
    )
