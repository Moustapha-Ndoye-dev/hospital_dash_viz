"""
Page Accueil — Vue d'ensemble et KPIs globaux.
Route : /
"""

import dash
from dash import html, dcc, callback, Input, Output
from utils.data_loader import load_data, apply_filters
from utils.statistics import compute_kpis, stats_par_departement, tendance_mensuelle
from components.kpi_card import kpi_card, stat_row
from components.charts import (
    donut_chart, line_chart, bar_horizontal, bar_vertical,
)
from config import DEPT_COLORS, CHART_PALETTE

dash.register_page(__name__, path="/", name="Accueil", title="Accueil | Dashboard Hospitalier")

# ═══════════════════════════════════════
# LAYOUT
# ═══════════════════════════════════════
layout = html.Div([
    # Header
    html.Div(className="page-header", children=[
        html.H1("📊 Vue d'ensemble", className="page-title"),
        html.P(
            "Synthèse des indicateurs clés de performance hospitalière",
            className="page-subtitle",
        ),
    ]),

    # KPIs
    html.Div(id="home-kpis", className="kpi-grid"),

    # Insight dynamique
    html.Div(id="home-insight"),

    # Graphiques ligne 1 : 2 colonnes
    html.Div(className="charts-grid", children=[
        html.Div(className="chart-card", children=[
            html.Div("📈 Admissions mensuelles", className="chart-title"),
            html.Div("Évolution du flux de patients sur la période", className="chart-subtitle"),
            dcc.Graph(id="home-line-admissions", config={"displayModeBar": False}),
            html.Div(id="home-advice-admissions")
        ]),
        html.Div(className="chart-card", children=[
            html.Div("🏥 Répartition par département", className="chart-title"),
            html.Div("Volume de patients par service hospitalier", className="chart-subtitle"),
            dcc.Graph(id="home-bar-dept", config={"displayModeBar": False}),
            html.Div(id="home-advice-dept")
        ]),
    ]),

    # Graphiques ligne 2 : 2 colonnes
    html.Div(className="charts-grid", children=[
        html.Div(className="chart-card", children=[
            html.Div("👤 Répartition par sexe", className="chart-title"),
            html.Div("Distribution hommes / femmes", className="chart-subtitle"),
            dcc.Graph(id="home-donut-sexe", config={"displayModeBar": False}),
            html.Div(id="home-advice-sexe")
        ]),
        html.Div(className="chart-card", children=[
            html.Div("🩺 Coût moyen par pathologie", className="chart-title"),
            html.Div("Comparatif du coût moyen de séjour", className="chart-subtitle"),
            dcc.Graph(id="home-bar-maladie-cout", config={"displayModeBar": False}),
            html.Div(id="home-advice-maladie")
        ]),
    ]),

    # Top départements par coût
    html.Div(className="charts-grid", children=[
        html.Div(className="chart-card", children=[
            html.Div("💰 Classement départements par coût total", className="chart-title"),
            html.Div("Impact financier cumulé par service", className="chart-subtitle"),
            html.Div(id="home-ranking-dept"),
            html.Div(id="home-advice-ranking")
        ]),
        html.Div(className="chart-card", children=[
            html.Div("⏱️ DMS par département", className="chart-title"),
            html.Div("Durée Moyenne de Séjour — indicateur d'efficience", className="chart-subtitle"),
            dcc.Graph(id="home-bar-dms", config={"displayModeBar": False}),
            html.Div(id="home-advice-dms")
        ]),
    ]),
])


# ═══════════════════════════════════════
# CALLBACKS
# ═══════════════════════════════════════

@callback(
    Output("home-kpis", "children"),
    Output("home-insight", "children"),
    Output("home-line-admissions", "figure"),
    Output("home-bar-dept", "figure"),
    Output("home-donut-sexe", "figure"),
    Output("home-bar-maladie-cout", "figure"),
    Output("home-ranking-dept", "children"),
    Output("home-bar-dms", "figure"),
    Output("home-advice-admissions", "children"),
    Output("home-advice-dept", "children"),
    Output("home-advice-sexe", "children"),
    Output("home-advice-maladie", "children"),
    Output("home-advice-ranking", "children"),
    Output("home-advice-dms", "children"),
    Input("filter-store", "data"),
)
def update_home(filters):
    df = load_data()
    df = apply_filters(df, filters)

    if len(df) == 0:
        empty_msg = html.Div("Aucune donnée pour les filtres sélectionnés.",
                             style={"textAlign": "center", "color": "#8A95A9", "padding": "40px"})
        import plotly.graph_objects as go
        empty_fig = go.Figure()
        empty_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        empty_adv = html.Div()
        return [], empty_msg, empty_fig, empty_fig, empty_fig, empty_fig, empty_msg, empty_fig, empty_adv, empty_adv, empty_adv, empty_adv, empty_adv, empty_adv

    kpis = compute_kpis(df)

    # ── KPI Cards ──
    kpi_cards = [
        kpi_card("Patients", f"{kpis['total_patients']:,}".replace(",", " "),
                 "🏥", "#0AEFB7",
                 f"Ratio H/F : {kpis['ratio_hommes']}% / {100 - kpis['ratio_hommes']}%"),
        kpi_card("Coût Total", f"{kpis['cout_total']:,} €".replace(",", " "),
                 "💰", "#34D399",
                 f"Moy: {kpis['cout_moyen']:,.0f} €".replace(",", " ")),
        kpi_card("DMS", f"{kpis['dms']} j",
                 "⏱️", "#FBBF24",
                 f"Coût/jour : {kpis['cout_par_jour']:,.0f} €".replace(",", " ")),
        kpi_card("Séjours longs", f"{kpis['taux_sejour_long']}%",
                 "📋", "#F87171",
                 f"{kpis['patients_critiques']} patients critiques (>7 000€)"),
        kpi_card("Âge moyen", f"{kpis['age_moyen']} ans",
                 "👤", "#A78BFA",
                 f"Indice gravité : {kpis['gravite_moyenne']:.3f}"),
    ]

    # ── Insight contextuel ──
    dept_stats = stats_par_departement(df)
    if len(dept_stats) > 0:
        top_dept = dept_stats.iloc[0]
        insight = html.Div(className="insight-box", children=[
            html.Div("🩺 Synthèse Médico-Administrative & Orientations", className="insight-title"),
            html.Div(f"👉 État des lieux : Le service '{top_dept['Departement']}' est le pôle de charge principal. Il rassemble un coût total de {top_dept['CoutTotal']:,.0f} €, traitant {int(top_dept['Patients'])} patients avec une DMS de {top_dept['DMS']:.1f} jours et un taux de séjours longs de {top_dept['TauxSejourLong']}%." , className="insight-text", style={"marginBottom": "8px"}),
            html.Div("💡 Actions recommandées : Priorisez un audit capacitaire sur ce service ciblé. Déployez des gestionnaires de lits (bed managers) pour anticiper les sorties hospitalières et désengorger le service.", className="insight-text", style={"fontWeight": "500", "color": "#F87171"})
        ])
    else:
        insight = html.Div()

    # ── Line chart admissions ──
    monthly = tendance_mensuelle(df)
    fig_line = line_chart(monthly, "AnneeMois", "Admissions",
                          title="", color="#0AEFB7", fill=True)
    fig_line.update_layout(height=340)

    # ── Bar chart départements ──
    dept_vol = df["Departement"].value_counts().reset_index()
    dept_vol.columns = ["Departement", "Patients"]
    fig_bar_dept = bar_horizontal(dept_vol, "Patients", "Departement",
                                  color="Departement", title="",
                                  color_map=DEPT_COLORS)
    fig_bar_dept.update_layout(height=340)

    # ── Donut sexe ──
    sexe_counts = df["Sexe"].value_counts()
    fig_donut = donut_chart(
        ["Hommes" if s == "M" else "Femmes" for s in sexe_counts.index],
        sexe_counts.values.tolist(),
        title="",
        colors=["#38BDF8", "#F472B6"],
    )
    fig_donut.update_layout(height=340)

    # ── Bar coût par maladie ──
    mal_cout = df.groupby("Maladie")["Cout"].mean().reset_index()
    mal_cout.columns = ["Maladie", "CoutMoyen"]
    fig_bar_mal = bar_vertical(mal_cout, "Maladie", "CoutMoyen",
                                color="Maladie", title="",
                                color_map=None)
    fig_bar_mal.update_layout(height=340, showlegend=False)
    fig_bar_mal.update_traces(
        marker_color=[CHART_PALETTE[i % len(CHART_PALETTE)]
                      for i in range(len(mal_cout))],
    )

    # ── Ranking départements ──
    if len(dept_stats) > 0:
        max_cout = dept_stats["CoutTotal"].max()
        ranking = [
            stat_row(
                row["Departement"],
                f"{row['CoutTotal']:,.0f} €".replace(",", " "),
                bar_pct=(row["CoutTotal"] / max_cout * 100) if max_cout > 0 else 0,
                color=DEPT_COLORS.get(row["Departement"], "#00B4D8"),
            )
            for _, row in dept_stats.iterrows()
        ]
    else:
        ranking = [html.Div("Aucune donnée")]

    # ── Bar DMS ──
    dms_dept = df.groupby("Departement")["DureeSejour"].mean().reset_index()
    dms_dept.columns = ["Departement", "DMS"]
    fig_dms = bar_vertical(dms_dept, "Departement", "DMS",
                            color="Departement", title="",
                            color_map=DEPT_COLORS)
    fig_dms.update_layout(height=340, showlegend=False)

    # -- EXPERT ADVICES DYNAMICS --
    if len(monthly) > 0:
        max_month = monthly.loc[monthly["Admissions"].idxmax(), "AnneeMois"]
        min_month = monthly.loc[monthly["Admissions"].idxmin(), "AnneeMois"]
        adv_admissions = html.Div([
            html.Strong("💡 Interprétation : "), f"L'afflux maximum a eu lieu en {max_month} et le minimum en {min_month}. ",
            html.Strong("Action : "), f"Concentrez les ressources intérimaires autour de la période de {max_month}."
        ], className="chart-expert-advice")
    else: adv_admissions = html.Div()
    
    if len(dept_vol) > 0:
        top_d = dept_vol.iloc[0]["Departement"]
        adv_dept = html.Div([
            html.Strong("💡 Interprétation : "), f"Le département '{top_d}' concentre la plus grosse cohorte de patients. ",
            html.Strong("Action : "), f"Initiez un audit capacitaire (nombre de lits) en '{top_d}' pour vérifier si la structure matérielle correspond à cette charge."
        ], className="chart-expert-advice")
    else: adv_dept = html.Div()

    if len(sexe_counts) > 0:
        dom_sexe = "Hommes" if sexe_counts.idxmax() == "M" else "Femmes"
        ratio = (sexe_counts.max() / sexe_counts.sum()) * 100
        adv_sexe = html.Div([
            html.Strong("💡 Interprétation : "), f"La patientèle est constituée à {ratio:.1f}% de {dom_sexe}. ",
            html.Strong("Action : "), "Ajustez les campagnes de santé publique (dépistage) en conséquence de ce sex-ratio marqué."
        ], className="chart-expert-advice")
    else: adv_sexe = html.Div()
    
    if len(mal_cout) > 0:
        mal_cout_sorted = mal_cout.sort_values("CoutMoyen", ascending=False)
        top_mc = mal_cout_sorted.iloc[0]["Maladie"]
        adv_maladie = html.Div([
            html.Strong("💡 Interprétation : "), f"Le traitement de '{top_mc}' est la pathologie requérant le plus haut budget unitaire. ",
            html.Strong("Action : "), f"Centralisez les achats (dispositifs, médicaments) liés à '{top_mc}' pour faire levier sur les fournisseurs."
        ], className="chart-expert-advice")
    else: adv_maladie = html.Div()
    
    if len(dept_stats) > 0:
        top_dc = dept_stats.iloc[0]["Departement"]
        adv_ranking = html.Div([
            html.Strong("💡 Interprétation : "), f"Au global, '{top_dc}' est le centre de coût principal de la sélection. ",
            html.Strong("Action : "), f"Affectez un contrôleur de gestion spécifiquement sur le parcours patient en '{top_dc}'."
        ], className="chart-expert-advice")
    else: adv_ranking = html.Div()
    
    if len(dms_dept) > 0:
        dms_max_dept = dms_dept.loc[dms_dept["DMS"].idxmax(), "Departement"]
        adv_dms = html.Div([
            html.Strong("💡 Interprétation : "), f"Le service de '{dms_max_dept}' enregistre le plus fort blocage de lits. ",
            html.Strong("Action : "), f"Planifiez une Revue de Morbi-Mortalité (RMM) sur les dossiers longs en '{dms_max_dept}'."
        ], className="chart-expert-advice")
    else: adv_dms = html.Div()

    return kpi_cards, insight, fig_line, fig_bar_dept, fig_donut, fig_bar_mal, ranking, fig_dms, adv_admissions, adv_dept, adv_sexe, adv_maladie, adv_ranking, adv_dms
