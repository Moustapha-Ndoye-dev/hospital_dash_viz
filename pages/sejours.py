"""
Page Séjours — Analyse des durées d'hospitalisation.
Route : /sejours
"""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.data_loader import load_data, apply_filters
from utils.filter_inputs import FILTER_INPUTS, build_filters_dict
from components.charts import (
    histogram, violin_plot, bar_vertical, line_chart, heatmap, donut_chart,
)
from components.kpi_card import kpi_card
from config import (
    DEPT_COLORS, TRAITEMENT_COLORS, CHART_PALETTE, PLOTLY_LAYOUT,
    JOURS_SEMAINE, MOIS_NOMS,
)

dash.register_page(__name__, path="/sejours", name="Séjours", title="Séjours | Dashboard Hospitalier")

layout = html.Div([
    html.Div(className="page-header", children=[
        html.H1("🏨 Analyse des Séjours", className="page-title"),
        html.P("Durées d'hospitalisation, saisonnalité et rotation", className="page-subtitle"),
    ]),

    html.Div(id="sej-kpis", className="kpi-grid"),
    html.Div(id="sej-insight"),

    # Ligne 1
    html.Div(className="charts-grid", children=[
        html.Div(className="chart-card", children=[
            html.Div("📊 Distribution des durées", className="chart-title"),
            html.Div("Répartition des séjours par nombre de jours", className="chart-subtitle"),
            dcc.Graph(id="sej-hist-duree", config={"displayModeBar": False}),
            html.Div(id="sej-advice-hist")
        ]),
        html.Div(className="chart-card", children=[
            html.Div("🎻 Durée par département", className="chart-title"),
            html.Div("Violin plot — distribution et médiane par service", className="chart-subtitle"),
            dcc.Graph(id="sej-violin-dept", config={"displayModeBar": False}),
            html.Div(id="sej-advice-violin")
        ]),
    ]),

    # Ligne 2
    html.Div(className="charts-grid", children=[
        html.Div(className="chart-card", children=[
            html.Div("🗓️ Heatmap admissions Mois × Jour", className="chart-title"),
            html.Div("Saisonnalité et patterns jour de la semaine", className="chart-subtitle"),
            dcc.Graph(id="sej-heatmap-mois-jour", config={"displayModeBar": False}),
            html.Div(id="sej-advice-heatmap")
        ]),
        html.Div(className="chart-card", children=[
            html.Div("📦 Catégories de séjour", className="chart-title"),
            html.Div("Ambulatoire, court, moyen, long", className="chart-subtitle"),
            dcc.Graph(id="sej-donut-categorie", config={"displayModeBar": False}),
            html.Div(id="sej-advice-cat")
        ]),
    ]),

    # Ligne 3
    html.Div(className="charts-grid", children=[
        html.Div(className="chart-card", children=[
            html.Div("💊 DMS par traitement", className="chart-title"),
            html.Div("Impact du type de traitement sur la durée", className="chart-subtitle"),
            dcc.Graph(id="sej-bar-traitement", config={"displayModeBar": False}),
            html.Div(id="sej-advice-trait")
        ]),
        html.Div(className="chart-card", children=[
            html.Div("📈 Tendance DMS mensuelle", className="chart-title"),
            html.Div("Évolution de la durée moyenne sur 12 mois", className="chart-subtitle"),
            dcc.Graph(id="sej-line-dms", config={"displayModeBar": False}),
            html.Div(id="sej-advice-line")
        ]),
    ]),

    # Ligne 4
    html.Div(className="charts-grid", children=[
        html.Div(className="chart-card", children=[
            html.Div("🌡️ DMS par saison", className="chart-title"),
            html.Div("Variation saisonnière des durées d'hospitalisation", className="chart-subtitle"),
            dcc.Graph(id="sej-bar-saison", config={"displayModeBar": False}),
            html.Div(id="sej-advice-saison")
        ]),
        html.Div(className="chart-card", children=[
            html.Div("🩺 Taux de séjour long par pathologie", className="chart-title"),
            html.Div("Pourcentage de séjours > 10 jours — indicateur de complexité", className="chart-subtitle"),
            dcc.Graph(id="sej-bar-taux-long", config={"displayModeBar": False}),
            html.Div(id="sej-advice-taux")
        ]),
    ]),
])


@callback(
    Output("sej-kpis", "children"),
    Output("sej-insight", "children"),
    Output("sej-hist-duree", "figure"),
    Output("sej-violin-dept", "figure"),
    Output("sej-heatmap-mois-jour", "figure"),
    Output("sej-donut-categorie", "figure"),
    Output("sej-bar-traitement", "figure"),
    Output("sej-line-dms", "figure"),
    Output("sej-bar-saison", "figure"),
    Output("sej-bar-taux-long", "figure"),
    Output("sej-advice-hist", "children"),
    Output("sej-advice-violin", "children"),
    Output("sej-advice-heatmap", "children"),
    Output("sej-advice-cat", "children"),
    Output("sej-advice-trait", "children"),
    Output("sej-advice-line", "children"),
    Output("sej-advice-saison", "children"),
    Output("sej-advice-taux", "children"),
    *FILTER_INPUTS,
)
def update_sejours(dept, maladie, sexe, age, traitement, date_start, date_end):
    filters = build_filters_dict(
        dept, maladie, sexe, age, traitement, date_start, date_end
    )
    df = load_data()
    df = apply_filters(df, filters)

    if len(df) == 0:
        empty = go.Figure().update_layout(**PLOTLY_LAYOUT)
        empty_adv = html.Div()
        return [], html.Div(), empty, empty, empty, empty, empty, empty, empty, empty, empty_adv, empty_adv, empty_adv, empty_adv, empty_adv, empty_adv, empty_adv, empty_adv

    dms = df["DureeSejour"].mean()
    median_dur = df["DureeSejour"].median()
    n_long = (df["DureeSejour"] > 10).sum()
    n_court = (df["DureeSejour"] <= 2).sum()

    # ── KPIs ──
    kpis = [
        kpi_card("DMS", f"{dms:.1f} j", "⏱️", "#00B4D8",
                 f"Médiane : {median_dur:.0f} jours"),
        kpi_card("Séjours longs", f"{n_long}", "📋", "#EF476F",
                 f"> 10 jours — {n_long / len(df) * 100:.1f}%"),
        kpi_card("Ambulatoires", f"{n_court}", "🚶", "#06D6A0",
                 f"≤ 2 jours — {n_court / len(df) * 100:.1f}%"),
        kpi_card("Jours total", f"{df['DureeSejour'].sum():,}".replace(",", " "),
                 "🗓️", "#FFD166",
                 f"Min: {df['DureeSejour'].min()}j — Max: {df['DureeSejour'].max()}j"),
    ]

    # ── Insight ──
    dept_dms = df.groupby("Departement")["DureeSejour"].mean()
    dept_max = dept_dms.idxmax()
    dept_min = dept_dms.idxmin()
    insight = html.Div(className="insight-box", children=[
        html.Div("🩺 Bilan Logistique Médicale & Orientations", className="insight-title"),
        html.Div(f"👉 État des lieux : La capacité de rotation globale d'un lit (DMS) est de {dms:.1f} jours. Le département {dept_max} marque un point dur avec un ralentissement notable des flux à {dept_dms.max():.1f} jours d'hospitalisation moyenne en continu.", className="insight-text", style={"marginBottom": "8px"}),
        html.Div(f"👉 Explication : À l'inverse, des spécialités optimisées ou intrinsèquement plus légères comme '{dept_min}' drainent leurs patients en seulement {dept_dms.min():.1f} jours, montrant l'efficience potentielle du Fast-Track ou de la chirurgie de semaine.", className="insight-text", style={"marginBottom": "8px"}),
        html.Div(f"💡 Actions recommandées : L'effondrement de la DMS d'un seul jour libérerait temporairement des budgets atteignant virtuellement {df['CoutParJour'].mean() * len(df):,.0f} €. Fixez des Réunions de Concertation Pluridisciplinaires (RCP) précoces en '{dept_max}' pour dé-complexifier la sortie.", className="insight-text", style={"fontWeight": "500", "color": "#14919B"})
    ])

    # ── Histogramme durée ──
    fig_hist = histogram(df, "DureeSejour", nbins=15, title="", color="#14919B")
    fig_hist.update_layout(height=360, xaxis_title="Durée (jours)", yaxis_title="Patients")

    # ── Violin département ──
    fig_violin = violin_plot(df, "Departement", "DureeSejour", title="", color_map=DEPT_COLORS)
    fig_violin.update_layout(height=360, yaxis_title="Durée (jours)")

    # ── Heatmap mois × jour ──
    heat_data = df.groupby(["NomMois", "NomJour"]).size().reset_index(name="Admissions")
    heat_pivot = heat_data.pivot_table(
        index="NomJour", columns="NomMois", values="Admissions", fill_value=0
    )
    # Ordonner les jours
    jours_order = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    mois_order = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
    heat_pivot = heat_pivot.reindex(index=[j for j in jours_order if j in heat_pivot.index],
                                     columns=[m for m in mois_order if m in heat_pivot.columns])
    fig_heatmap = heatmap(heat_pivot, title="", colorscale="YlGnBu")
    fig_heatmap.update_layout(height=360)

    # ── Donut catégorie séjour ──
    cat_counts = df["CategorieSejour"].value_counts()
    fig_donut = donut_chart(
        cat_counts.index.tolist(),
        cat_counts.values.tolist(),
        title="",
        colors=["#34D399", "#14919B", "#FBBF24", "#F87171"],
    )
    fig_donut.update_layout(height=360)

    # ── Bar DMS par traitement ──
    dms_trait = df.groupby("Traitement")["DureeSejour"].mean().round(1).reset_index()
    dms_trait.columns = ["Traitement", "DMS"]
    dms_trait = dms_trait.sort_values("DMS", ascending=False)
    fig_trait = bar_vertical(dms_trait, "Traitement", "DMS",
                              color="Traitement", title="",
                              color_map=TRAITEMENT_COLORS)
    fig_trait.update_layout(height=360, yaxis_title="DMS (jours)")

    # ── Line tendance DMS ──
    monthly_dms = df.groupby("AnneeMois")["DureeSejour"].mean().round(1).reset_index()
    monthly_dms.columns = ["AnneeMois", "DMS"]
    fig_line_dms = line_chart(monthly_dms, "AnneeMois", "DMS",
                               title="", color="#FBBF24", fill=False)
    fig_line_dms.update_layout(height=360, yaxis_title="DMS (jours)")

    # ── Bar DMS par saison ──
    saison_dms = df.groupby("Saison")["DureeSejour"].mean().round(1).reset_index()
    saison_dms.columns = ["Saison", "DMS"]
    saison_order = ["Hiver", "Printemps", "Été", "Automne"]
    saison_dms["Saison"] = pd.Categorical(saison_dms["Saison"], categories=saison_order, ordered=True)
    saison_dms = saison_dms.sort_values("Saison")
    fig_saison = bar_vertical(saison_dms, "Saison", "DMS", title="",
                               color_map=None)
    fig_saison.update_traces(marker_color=["#38BDF8", "#34D399", "#FBBF24", "#F87171"])
    fig_saison.update_layout(height=360, showlegend=False, yaxis_title="DMS (jours)")

    # ── Bar taux séjour long par pathologie ──
    taux_long = df.groupby("Maladie").apply(
        lambda x: round((x["DureeSejour"] > 10).sum() / len(x) * 100, 1)
    ).reset_index(name="TauxLong")
    taux_long = taux_long.sort_values("TauxLong", ascending=False)
    fig_taux = bar_vertical(taux_long, "Maladie", "TauxLong", title="",
                             color_map=None)
    fig_taux.update_traces(marker_color=CHART_PALETTE[:len(taux_long)])
    fig_taux.update_layout(height=360, showlegend=False, yaxis_title="% séjours > 10j")

    # -- EXPERT ADVICES DYNAMICS --
    if n_long > 0:
        pct_long = (n_long / len(df)) * 100
        adv_hist = html.Div([
            html.Strong("💡 Interprétation : "), f"Les {n_long} séjours excédant 10 jours représentent la 'traîne' logistique ({pct_long:.1f}%). ",
            html.Strong("Action : "), "Faites intervenir le service social dès le Jour 6 pour ces profils afin d'éviter la situation de malade bloqué."
        ], className="chart-expert-advice")
    else: adv_hist = html.Div()

    if len(dept_dms) > 0:
        worst_dept = dept_dms.idxmax()
        adv_violin = html.Div([
            html.Strong("💡 Interprétation : "), f"'{worst_dept}' présente la forme la plus étirée, indiquant une incapacité forte à prévoir la date de sortie. ",
            html.Strong("Action : "), f"Concentrez le pôle 'Bed Management' exclusivement sur les lits de courte durée de '{worst_dept}'."
        ], className="chart-expert-advice")
    else: adv_violin = html.Div()

    if len(heat_data) > 0:
        top_heat = heat_data.loc[heat_data["Admissions"].idxmax()]
        adv_heatmap = html.Div([
            html.Strong("💡 Interprétation : "), f"Le pic d'admission croisé historique se trouve le {top_heat['NomJour']} du mois de {top_heat['NomMois']}. ",
            html.Strong("Action : "), f"Sanctuarisez ce créneau : aucune RTT ou formation médicale ne doit être validée les {top_heat['NomJour']}s de {top_heat['NomMois']}."
        ], className="chart-expert-advice")
    else: adv_heatmap = html.Div()
    
    if len(cat_counts) > 0:
        dom_cat = cat_counts.idxmax()
        adv_cat = html.Div([
            html.Strong("💡 Interprétation : "), f"L'hôpital est principalement orienté vers le séjour de type '{dom_cat}'. ",
            html.Strong("Action : "), f"Si '{dom_cat}' n'est pas 'Ambulatoire', vous ne répondez pas aux injonctions de l'ARS concernant le virage ambulatoire."
        ], className="chart-expert-advice")
    else: adv_cat = html.Div()
    
    if len(dms_trait) > 0:
        top_dms_t = dms_trait.iloc[0]["Traitement"]
        adv_trait = html.Div([
            html.Strong("💡 Interprétation : "), f"L'acte / traitement '{top_dms_t}' est le plus délétère pour la rotation des lits. ",
            html.Strong("Action : "), f"Investiguez de nouvelles techniques mini-invasives permettant de raccourcir la convalescence post-'{top_dms_t}'."
        ], className="chart-expert-advice")
    else: adv_trait = html.Div()
    
    if len(monthly_dms) > 0:
        pic_dms = monthly_dms.loc[monthly_dms["DMS"].idxmax()]
        adv_line = html.Div([
            html.Strong("💡 Interprétation : "), f"Le pic d'engorgement a été atteint en {pic_dms['AnneeMois']} avec {pic_dms['DMS']:.1f} jours en moyenne. ",
            html.Strong("Action : "), f"Ce mois critique nécessite systématiquement l'activation d'un 'Plan Blanc' de niveau 1 capacitaire."
        ], className="chart-expert-advice")
    else: adv_line = html.Div()
    
    if len(saison_dms) > 0:
        worst_saison = saison_dms.loc[saison_dms["DMS"].idxmax()]
        adv_saison = html.Div([
            html.Strong("💡 Interprétation : "), f"La saison '{worst_saison['Saison']}' concentre les durées les plus longues ({worst_saison['DMS']:.1f} j). ",
            html.Strong("Action : "), f"Limitez les admissions programmées complexes durant '{worst_saison['Saison']}' pour préserver la capacité de réponse aux urgences aiguës."
        ], className="chart-expert-advice")
    else: adv_saison = html.Div()
    
    if len(taux_long) > 0:
        top_long = taux_long.iloc[0]
        adv_taux = html.Div([
            html.Strong("💡 Interprétation : "), f"La pathologie '{top_long['Maladie']}' génère des séjours bloquants dans {top_long['TauxLong']}% des cas. ",
            html.Strong("Action : "), f"Désignez un médecin coordonnateur spécifiquement affecté à la filière de retour à domicile pour '{top_long['Maladie']}'."
        ], className="chart-expert-advice")
    else: adv_taux = html.Div()

    return kpis, insight, fig_hist, fig_violin, fig_heatmap, fig_donut, fig_trait, fig_line_dms, fig_saison, fig_taux, adv_hist, adv_violin, adv_heatmap, adv_cat, adv_trait, adv_line, adv_saison, adv_taux
