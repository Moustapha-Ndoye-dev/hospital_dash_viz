"""
Charts — Fonctions de création de graphiques Plotly.
Template unifié et style professionnel pour tous les graphiques.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    PLOTLY_LAYOUT, CHART_PALETTE, DEPT_COLORS,
    MALADIE_COLORS, TRAITEMENT_COLORS, COLORS,
)


def _apply_theme(fig: go.Figure) -> go.Figure:
    """Applique le thème sombre médical à un graphique."""
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


# ═══════════════════════════════════════════════════
# BARRES
# ═══════════════════════════════════════════════════

def bar_horizontal(df: pd.DataFrame, x: str, y: str,
                   color: str = None, title: str = "",
                   color_map: dict = None) -> go.Figure:
    """Bar chart horizontal trié par valeur."""
    df_sorted = df.sort_values(x, ascending=True)
    fig = px.bar(
        df_sorted, x=x, y=y, orientation="h",
        color=y if color is None else color,
        color_discrete_map=color_map or DEPT_COLORS,
        title=title,
    )
    fig.update_traces(
        marker_line_width=0,
        texttemplate="%{x:,.0f}", textposition="outside",
        textfont=dict(size=10, color="#7B8FA3"),
    )
    fig.update_layout(showlegend=False)
    return _apply_theme(fig)


def bar_vertical(df: pd.DataFrame, x: str, y: str,
                 color: str = None, title: str = "",
                 color_map: dict = None) -> go.Figure:
    """Bar chart vertical."""
    fig = px.bar(
        df, x=x, y=y,
        color=color or x,
        color_discrete_map=color_map or DEPT_COLORS,
        title=title,
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(showlegend=False)
    return _apply_theme(fig)


def bar_grouped(df: pd.DataFrame, x: str, y: str,
                color: str = "", title: str = "",
                color_map: dict = None, barmode: str = "group") -> go.Figure:
    """Bar chart groupé ou empilé."""
    fig = px.bar(
        df, x=x, y=y, color=color,
        color_discrete_map=color_map,
        title=title, barmode=barmode,
    )
    fig.update_traces(marker_line_width=0)
    return _apply_theme(fig)


# ═══════════════════════════════════════════════════
# CIRCULAIRES
# ═══════════════════════════════════════════════════

def donut_chart(labels: list, values: list, title: str = "",
                colors: list = None, hole: float = 0.55) -> go.Figure:
    """Donut chart avec trou central."""
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=hole,
        marker=dict(
            colors=colors or CHART_PALETTE,
            line=dict(color="#060A0F", width=2),
        ),
        textinfo="label+percent",
        textfont=dict(size=10, color="#E4ECF4", family="DM Sans, sans-serif"),
        hovertemplate="<b>%{label}</b><br>%{value} patients<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(title=title)
    return _apply_theme(fig)


def sunburst_chart(df: pd.DataFrame, path: list,
                   values: str = None, title: str = "",
                   color_map: dict = None) -> go.Figure:
    """Sunburst hiérarchique."""
    fig = px.sunburst(
        df, path=path, values=values,
        color=path[0] if color_map else None,
        color_discrete_map=color_map,
        title=title,
    )
    fig.update_traces(
        textfont=dict(size=11),
        insidetextorientation="radial",
    )
    return _apply_theme(fig)


def treemap_chart(df: pd.DataFrame, path: list,
                  values: str = None, title: str = "",
                  color_map: dict = None) -> go.Figure:
    """Treemap hiérarchique."""
    fig = px.treemap(
        df, path=path, values=values,
        color=path[0] if color_map else None,
        color_discrete_map=color_map,
        title=title,
    )
    fig.update_traces(
        textfont=dict(size=12),
        marker_line_width=1,
        marker_line_color="#060A0F",
    )
    return _apply_theme(fig)


# ═══════════════════════════════════════════════════
# LIGNES / AIRES
# ═══════════════════════════════════════════════════

def line_chart(df: pd.DataFrame, x: str, y: str,
               title: str = "", color: str = "#0AEFB7",
               fill: bool = False) -> go.Figure:
    """Graphique en ligne avec option aire remplie."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x], y=df[y],
        mode="lines+markers",
        line=dict(color=color, width=2, shape="spline"),
        marker=dict(size=5, color=color, line=dict(width=1, color="#060A0F")),
        fill="tozeroy" if fill else None,
        fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.1)" if fill else None,
        hovertemplate="<b>%{x}</b><br>%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(title=title)
    return _apply_theme(fig)


def multi_line_chart(df: pd.DataFrame, x: str, y_cols: list,
                     title: str = "", colors: list = None) -> go.Figure:
    """Multi lignes sur le même graphique."""
    fig = go.Figure()
    palette = colors or CHART_PALETTE
    for i, col in enumerate(y_cols):
        fig.add_trace(go.Scatter(
            x=df[x], y=df[col],
            name=col,
            mode="lines+markers",
            line=dict(color=palette[i % len(palette)], width=2),
            marker=dict(size=5),
        ))
    fig.update_layout(title=title)
    return _apply_theme(fig)


# ═══════════════════════════════════════════════════
# DISTRIBUTIONS
# ═══════════════════════════════════════════════════

def histogram(df: pd.DataFrame, x: str, nbins: int = 20,
              title: str = "", color: str = "#14919B") -> go.Figure:
    """Histogramme de distribution."""
    fig = px.histogram(
        df, x=x, nbins=nbins, title=title,
        color_discrete_sequence=[color],
    )
    fig.update_traces(
        marker_line_width=1,
        marker_line_color="#060A0F",
    )
    fig.update_layout(bargap=0.05)
    return _apply_theme(fig)


def box_plot(df: pd.DataFrame, x: str, y: str,
             title: str = "", color_map: dict = None) -> go.Figure:
    """Boîte à moustaches par catégorie."""
    fig = px.box(
        df, x=x, y=y, color=x,
        color_discrete_map=color_map or DEPT_COLORS,
        title=title,
    )
    fig.update_traces(
        marker=dict(size=3, opacity=0.5),
        line=dict(width=1.5),
    )
    fig.update_layout(showlegend=False)
    return _apply_theme(fig)


def violin_plot(df: pd.DataFrame, x: str, y: str,
                title: str = "", color_map: dict = None) -> go.Figure:
    """Violin plot par catégorie."""
    fig = px.violin(
        df, x=x, y=y, color=x, box=True, points="outliers",
        color_discrete_map=color_map or DEPT_COLORS,
        title=title,
    )
    fig.update_layout(showlegend=False)
    return _apply_theme(fig)


# ═══════════════════════════════════════════════════
# SCATTER
# ═══════════════════════════════════════════════════

def scatter_plot(df: pd.DataFrame, x: str, y: str,
                 color: str = None, size: str = None,
                 title: str = "", color_map: dict = None,
                 trendline: str = None) -> go.Figure:
    """Scatter plot avec tendance optionnelle (OLS via statsmodels, voir requirements.txt)."""
    try:
        fig = px.scatter(
            df, x=x, y=y, color=color, size=size,
            color_discrete_map=color_map or DEPT_COLORS,
            title=title, trendline=trendline,
            opacity=0.7,
        )
    except Exception:
        if not trendline:
            raise
        fig = px.scatter(
            df, x=x, y=y, color=color, size=size,
            color_discrete_map=color_map or DEPT_COLORS,
            title=title, trendline=None,
            opacity=0.7,
        )
    fig.update_traces(marker=dict(line=dict(width=0.5, color="#060A0F")))
    return _apply_theme(fig)


# ═══════════════════════════════════════════════════
# HEATMAP
# ═══════════════════════════════════════════════════

def heatmap(matrix: pd.DataFrame, title: str = "",
            colorscale: str = "Blues") -> go.Figure:
    """Heatmap / carte de chaleur."""
    fig = go.Figure(go.Heatmap(
        z=matrix.values,
        x=matrix.columns.tolist(),
        y=matrix.index.tolist(),
        colorscale=colorscale,
        text=matrix.values.round(0).astype(int),
        texttemplate="%{text}",
        textfont=dict(size=10, color="#E4ECF4"),
        hovertemplate="<b>%{y}</b> × <b>%{x}</b><br>Valeur: %{z:,.0f}<extra></extra>",
        colorbar=dict(
            tickfont=dict(color="#7B8FA3"),
            title=dict(font=dict(color="#7B8FA3")),
        ),
    ))
    fig.update_layout(title=title)
    return _apply_theme(fig)


# ═══════════════════════════════════════════════════
# RADAR
# ═══════════════════════════════════════════════════

def radar_chart(categories: list, values: list,
                title: str = "", color: str = "#0AEFB7",
                fill: bool = True) -> go.Figure:
    """Radar / spider chart."""
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself" if fill else None,
        fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.12)",
        line=dict(color=color, width=2),
        marker=dict(size=4, color=color),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                gridcolor="rgba(255,255,255,0.06)",
                tickfont=dict(size=9, color="#7B8FA3"),
            ),
            angularaxis=dict(
                gridcolor="rgba(255,255,255,0.06)",
                tickfont=dict(size=10, color="#E4ECF4"),
            ),
        ),
        title=title,
    )
    return _apply_theme(fig)


# ═══════════════════════════════════════════════════
# INDICATEUR JAUGE
# ═══════════════════════════════════════════════════

def gauge_chart(value: float, title: str = "",
                min_val: float = 0, max_val: float = 100,
                suffix: str = "%",
                thresholds: dict = None) -> go.Figure:
    """Indicateur en jauge circulaire."""
    if thresholds is None:
        thresholds = {"green": 30, "yellow": 60, "red": 100}

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(suffix=suffix, font=dict(size=28, color="#E4ECF4", family="Outfit")),
        title=dict(text=title, font=dict(size=12, color="#7B8FA3", family="Outfit")),
        gauge=dict(
            axis=dict(range=[min_val, max_val], tickfont=dict(color="#7B8FA3")),
            bar=dict(color="#0AEFB7"),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            steps=[
                dict(range=[min_val, thresholds["green"]], color="rgba(52,211,153,0.15)"),
                dict(range=[thresholds["green"], thresholds["yellow"]], color="rgba(251,191,36,0.15)"),
                dict(range=[thresholds["yellow"], max_val], color="rgba(248,113,113,0.15)"),
            ],
        ),
    ))
    return _apply_theme(fig)
