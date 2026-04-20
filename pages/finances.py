"""
Page Finances — Analyse des coûts de séjour.
Route : /finances
"""

import dash
from dash import html, dcc, callback, Input, Output, dash_table
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import load_data, apply_filters
from utils.filter_inputs import FILTER_INPUTS, build_filters_dict
from utils.statistics import (
    compute_kpis, stats_par_departement, stats_par_maladie,
    top_sejours_couteux, distribution_stats, tendance_mensuelle,
)
from components.charts import (
    bar_horizontal, box_plot, scatter_plot, line_chart, histogram, gauge_chart,
)
from components.kpi_card import kpi_card
from config import DEPT_COLORS, MALADIE_COLORS, CHART_PALETTE, PLOTLY_LAYOUT, COLORS

dash.register_page(__name__, path="/finances", name="Finances", title="Finances | Dashboard Hospitalier")

layout = html.Div([
    html.Div(className="page-header", children=[
        html.H1("💰 Analyse Financière", className="page-title"),
        html.P("Coûts de séjour, efficience budgétaire et projections", className="page-subtitle"),
    ]),

    html.Div(id="fin-kpis", className="kpi-grid"),
    html.Div(id="fin-insight"),

    # Ligne 1
    html.Div(className="charts-grid", children=[
        html.Div(className="chart-card", children=[
            html.Div("📊 Distribution des coûts", className="chart-title"),
            html.Div("Répartition des montants de séjour", className="chart-subtitle"),
            dcc.Graph(id="fin-hist-cout", config={"displayModeBar": False}),
            html.Div(id="fin-advice-hist")
        ]),
        html.Div(className="chart-card", children=[
            html.Div("🔗 Corrélation Coût vs Durée", className="chart-title"),
            html.Div("r = 0.91 — Facteur prédictif principal", className="chart-subtitle"),
            dcc.Graph(id="fin-scatter-cout-duree", config={"displayModeBar": False}),
            html.Div(id="fin-advice-scatter")
        ]),
    ]),

    # Ligne 2
    html.Div(className="charts-grid", children=[
        html.Div(className="chart-card", children=[
            html.Div("🏥 Coût moyen par département", className="chart-title"),
            html.Div("Benchmarking inter-services", className="chart-subtitle"),
            dcc.Graph(id="fin-bar-cout-dept", config={"displayModeBar": False}),
            html.Div(id="fin-advice-dept")
        ]),
        html.Div(className="chart-card", children=[
            html.Div("🩺 Coûts par pathologie", className="chart-title"),
            html.Div("Dispersion des charges par maladie", className="chart-subtitle"),
            dcc.Graph(id="fin-box-cout-maladie", config={"displayModeBar": False}),
            html.Div(id="fin-advice-maladie")
        ]),
    ]),

    # Ligne 3
    html.Div(className="charts-grid", children=[
        html.Div(className="chart-card", children=[
            html.Div("📈 Coût cumulé mensuel", className="chart-title"),
            html.Div("Trajectoire budgétaire sur la période", className="chart-subtitle"),
            dcc.Graph(id="fin-line-cumule", config={"displayModeBar": False}),
            html.Div(id="fin-advice-cumule")
        ]),
        html.Div(className="chart-card", children=[
            html.Div("💎 Coût par journée €/j", className="chart-title"),
            html.Div("Indicateur d'efficience par département", className="chart-subtitle"),
            dcc.Graph(id="fin-bar-cout-jour", config={"displayModeBar": False}),
            html.Div(id="fin-advice-cout-jour")
        ]),
    ]),

    # Top 10 séjours coûteux
    html.Div(className="chart-card", children=[
        html.Div("🏆 Top 10 séjours les plus coûteux", className="chart-title"),
        html.Div("Identification des cas à fort impact budgétaire", className="chart-subtitle"),
        html.Div(id="fin-table-top10"),
    ]),
])


@callback(
    Output("fin-kpis", "children"),
    Output("fin-insight", "children"),
    Output("fin-hist-cout", "figure"),
    Output("fin-scatter-cout-duree", "figure"),
    Output("fin-bar-cout-dept", "figure"),
    Output("fin-box-cout-maladie", "figure"),
    Output("fin-line-cumule", "figure"),
    Output("fin-bar-cout-jour", "figure"),
    Output("fin-table-top10", "children"),
    Output("fin-advice-hist", "children"),
    Output("fin-advice-scatter", "children"),
    Output("fin-advice-dept", "children"),
    Output("fin-advice-maladie", "children"),
    Output("fin-advice-cumule", "children"),
    Output("fin-advice-cout-jour", "children"),
    *FILTER_INPUTS,
)
def update_finances(dept, maladie, sexe, age, traitement, date_start, date_end):
    filters = build_filters_dict(
        dept, maladie, sexe, age, traitement, date_start, date_end
    )
    df = load_data()
    df = apply_filters(df, filters)

    if len(df) == 0:
        empty = go.Figure().update_layout(**PLOTLY_LAYOUT)
        msg = html.Div("Aucune donnée", style={"color": "#7B8FA3", "padding": "20px"})
        empty_adv = html.Div()
        return [], msg, empty, empty, empty, empty, empty, empty, msg, empty_adv, empty_adv, empty_adv, empty_adv, empty_adv, empty_adv

    kpis_data = compute_kpis(df)
    cost_stats = distribution_stats(df["Cout"])

    # ── KPIs financiers ──
    kpis = [
        kpi_card("Coût Total", f"{kpis_data['cout_total']:,} €".replace(",", " "),
                 "💰", "#34D399",
                 f"Budget global de la période"),
        kpi_card("Coût Moyen", f"{kpis_data['cout_moyen']:,.0f} €".replace(",", " "),
                 "📊", "#14919B",
                 f"Médiane : {cost_stats['median']:,.0f} €".replace(",", " ")),
        kpi_card("Coût / Jour", f"{kpis_data['cout_par_jour']:,.0f} €".replace(",", " "),
                 "📅", "#FBBF24",
                 "Efficience par journée d'hospitalisation"),
        kpi_card("Écart-type", f"{cost_stats['std']:,.0f} €".replace(",", " "),
                 "📐", "#A78BFA",
                 f"IQR : {cost_stats['iqr']:,.0f} €".replace(",", " ")),
        kpi_card("Cas critiques", f"{kpis_data['patients_critiques']}",
                 "🚨", "#F87171",
                 f"Séjours > 7 000 € ({kpis_data['patients_critiques'] / len(df) * 100:.1f}%)"),
    ]

    # ── Insight ──
    corr = df["DureeSejour"].corr(df["Cout"])
    insight = html.Div(className="insight-box success", children=[
        html.Div("🩺 Analyse Médico-Économique & Recommandations", className="insight-title"),
        html.Div(f"👉 Diagnostic Financier : La corrélation entre la durée de l'hospitalisation et le coût direct est qualifiée de très forte (r = {corr:.2f}). Ce ratio démontre que la technologie et les actes médicaux ont un rôle financier secondaire face à l'hôtellerie hospitalière.", className="insight-text", style={"marginBottom": "8px"}),
        html.Div(f"👉 Explication : Conséquence directe, chaque journée de blocage d'un lit engendre un coût d'opportunité sévère d'environ {kpis_data['cout_par_jour']:,.0f} € et retarde la prise en charge des flux d'Urgences.", className="insight-text", style={"marginBottom": "8px"}),
        html.Div("💡 Actions recommandées : Il est impératif d'intégrer les directeurs d'EHPAD et de Soins de Suite (SSR) au comité stratégique, pour structurer des filières directes de transferts, coupant de fait les dépassements de séjour.", className="insight-text", style={"fontWeight": "500", "color": "#0AEFB7"})
    ])

    # ── Histogramme coûts ──
    fig_hist = histogram(df, "Cout", nbins=25, title="", color="#34D399")
    fig_hist.update_layout(height=360, xaxis_title="Coût (€)", yaxis_title="Patients")

    # ── Scatter coût vs durée ──
    fig_scatter = scatter_plot(df, "DureeSejour", "Cout", color="Departement",
                               title="", color_map=DEPT_COLORS, trendline="ols")
    fig_scatter.update_layout(height=360, xaxis_title="Durée de séjour (jours)",
                               yaxis_title="Coût (€)")

    # ── Bar coût par département ──
    dept_stats = stats_par_departement(df)
    fig_bar_dept = bar_horizontal(dept_stats, "CoutMoyen", "Departement",
                                   color="Departement", title="",
                                   color_map=DEPT_COLORS)
    fig_bar_dept.update_layout(height=360)

    # ── Box plot coût par maladie ──
    fig_box = box_plot(df, "Maladie", "Cout", title="", color_map=MALADIE_COLORS)
    fig_box.update_layout(height=360, yaxis_title="Coût (€)")

    # ── Line coût cumulé ──
    monthly = tendance_mensuelle(df)
    fig_cumule = line_chart(monthly, "AnneeMois", "CoutCumule",
                             title="", color="#34D399", fill=True)
    fig_cumule.update_layout(height=360, yaxis_title="Coût cumulé (€)")

    # ── Bar coût par jour par département ──
    cout_jour_dept = df.groupby("Departement")["CoutParJour"].mean().round(0).reset_index()
    cout_jour_dept.columns = ["Departement", "CoutParJour"]
    cout_jour_dept = cout_jour_dept.sort_values("CoutParJour", ascending=True)
    fig_cout_jour = bar_horizontal(cout_jour_dept, "CoutParJour", "Departement",
                                    color="Departement", title="",
                                    color_map=DEPT_COLORS)
    fig_cout_jour.update_layout(height=360)

    # ── Table top 10 ──
    top10 = top_sejours_couteux(df, n=10)
    table = dash_table.DataTable(
        data=top10.to_dict("records"),
        columns=[
            {"name": "ID", "id": "PatientID"},
            {"name": "Âge", "id": "Age"},
            {"name": "Sexe", "id": "Sexe"},
            {"name": "Département", "id": "Departement"},
            {"name": "Maladie", "id": "Maladie"},
            {"name": "Durée (j)", "id": "DureeSejour"},
            {"name": "Coût (€)", "id": "Cout", "type": "numeric",
             "format": {"specifier": ",.0f"}},
            {"name": "Traitement", "id": "Traitement"},
            {"name": "€/jour", "id": "CoutParJour", "type": "numeric",
             "format": {"specifier": ",.0f"}},
        ],
        style_header={
            "backgroundColor": COLORS["surface_light"],
            "color": COLORS["text_secondary"],
            "fontWeight": "600",
            "fontSize": "10px",
            "textTransform": "uppercase",
            "letterSpacing": "0.5px",
            "border": f"1px solid {COLORS['card_border']}",
        },
        style_cell={
            "backgroundColor": COLORS["surface"],
            "color": COLORS["text"],
            "fontSize": "12px",
            "border": f"1px solid rgba(255,255,255,0.04)",
            "padding": "10px 12px",
            "fontFamily": "DM Sans, sans-serif",
        },
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": COLORS["surface_light"],
            },
        ],
        sort_action="native",
        page_size=10,
    )

    # -- EXPERT ADVICES DYNAMICS --
    if cost_stats['iqr'] > 0:
        adv_hist = html.Div([
            html.Strong("💡 Interprétation : "), f"Le cœur de votre activité (IQR) fluctue de {cost_stats['iqr']:,.0f} €. ",
            html.Strong("Action : "), "Votre plateau technique doit être dimensionné financièrement pour amortir cette volatilité inter-patients constante."
        ], className="chart-expert-advice")
    else: adv_hist = html.Div()

    if len(df) > 0:
        corr_val = df["DureeSejour"].corr(df["Cout"])
        adv_scatter = html.Div([
            html.Strong("💡 Interprétation : "), f"Corrélation calculée : {corr_val:.2f}. La part 'hôtelière' justifie la majorité de la facturation hospitalière. ",
            html.Strong("Action : "), "Concentrez tous les efforts de réduction de coût non pas sur les dispositifs médicaux, mais sur la vitesse de prise en charge pour baisser la DMS."
        ], className="chart-expert-advice")
    else: adv_scatter = html.Div()

    if len(dept_stats) > 0:
        top_d_cost = dept_stats.iloc[0]["Departement"]
        adv_dept = html.Div([
            html.Strong("💡 Interprétation : "), f"Le département '{top_d_cost}' consomme la plus grosse enveloppe absolue. ",
            html.Strong("Action : "), f"Vérifiez que la base MCO annuelle (crédits alloués par la tutelle) compense bien la charge de '{top_d_cost}'."
        ], className="chart-expert-advice")
    else: adv_dept = html.Div()

    if len(df) > 0:
        std_mal = df.groupby("Maladie")["Cout"].std().dropna()
        if len(std_mal) > 0:
            var_mal = std_mal.idxmax()
            adv_maladie = html.Div([
                html.Strong("💡 Interprétation : "), f"La pathologie '{var_mal}' affiche la variance (boîte la plus large) la plus imprévisible. ",
                html.Strong("Action : "), f"Convoquez un staff multidisciplinaire pour homogénéiser les protocoles de prescription sur '{var_mal}'."
            ], className="chart-expert-advice")
        else: adv_maladie = html.Div()
    else: adv_maladie = html.Div()

    if len(monthly) > 0:
        delta = monthly.iloc[-1]["CoutCumule"]
        adv_cumule = html.Div([
            html.Strong("💡 Interprétation : "), f"L'atterrissage financier s'établit à {delta:,.0f} € sur cet exercice visuel. ",
            html.Strong("Action : "), "Vérifiez immédiatement cet atterrissage par rapport au budget prévisionnel de l'EPRD (État Prévisionnel des Recettes et Dépenses)."
        ], className="chart-expert-advice")
    else: adv_cumule = html.Div()

    if len(cout_jour_dept) > 0:
        top_efficience = cout_jour_dept.iloc[0]["Departement"]
        adv_cout_jour = html.Div([
            html.Strong("💡 Interprétation : "), f"'{top_efficience}' affiche le coût/jour le plus bas (efficience théorique maximale). ",
            html.Strong("Action : "), f"Inspectez '{top_efficience}' : ce coût bas est-il signe d'excellents process ou, au contraire, d'un sous-effectif chronique dangereux ?"
        ], className="chart-expert-advice")
    else: adv_cout_jour = html.Div()

    return kpis, insight, fig_hist, fig_scatter, fig_bar_dept, fig_box, fig_cumule, fig_cout_jour, table, adv_hist, adv_scatter, adv_dept, adv_maladie, adv_cumule, adv_cout_jour
