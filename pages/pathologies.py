"""
Page Pathologies — Analyse par maladie et traitement.
Route : /pathologies
"""

import dash
from dash import html, dcc, callback, Input, Output
import pandas as pd
from utils.data_loader import load_data, apply_filters
from utils.filter_inputs import FILTER_INPUTS, build_filters_dict
from utils.statistics import stats_par_maladie, stats_par_traitement, matrice_maladie_departement
from components.charts import (
    treemap_chart, heatmap, sunburst_chart, bar_grouped, radar_chart, donut_chart,
)
from components.kpi_card import kpi_card
from config import MALADIE_COLORS, TRAITEMENT_COLORS, CHART_PALETTE, PLOTLY_LAYOUT, DEPT_COLORS

dash.register_page(__name__, path="/pathologies", name="Pathologies", title="Pathologies | Dashboard Hospitalier")

layout = html.Div([
    html.Div(className="page-header", children=[
        html.H1("🩺 Analyse des Pathologies", className="page-title"),
        html.P("Prévalence, coûts et traitements par maladie", className="page-subtitle"),
    ]),

    html.Div(id="patho-kpis", className="kpi-grid"),
    html.Div(id="patho-insight"),

    # Ligne 1
    html.Div(className="charts-grid", children=[
        html.Div(className="chart-card", children=[
            html.Div("🗺️ Treemap Département → Pathologie", className="chart-title"),
            html.Div("Hiérarchie des cas par service et maladie", className="chart-subtitle"),
            dcc.Graph(id="patho-treemap", config={"displayModeBar": False}),
            html.Div(id="patho-advice-treemap")
        ]),
        html.Div(className="chart-card", children=[
            html.Div("☀️ Sunburst Dép. → Maladie → Traitement", className="chart-title"),
            html.Div("Vue hiérarchique complète du parcours patient", className="chart-subtitle"),
            dcc.Graph(id="patho-sunburst", config={"displayModeBar": False}),
            html.Div(id="patho-advice-sunburst")
        ]),
    ]),

    # Ligne 2
    html.Div(className="charts-grid", children=[
        html.Div(className="chart-card", children=[
            html.Div("🔥 Heatmap Maladie × Département", className="chart-title"),
            html.Div("Coût moyen par croisement pathologie / service", className="chart-subtitle"),
            dcc.Graph(id="patho-heatmap", config={"displayModeBar": False}),
            html.Div(id="patho-advice-heatmap")
        ]),
        html.Div(className="chart-card", children=[
            html.Div("🎯 Radar comparatif des pathologies", className="chart-title"),
            html.Div("Score normalisé sur les dimensions clés", className="chart-subtitle"),
            dcc.Graph(id="patho-radar", config={"displayModeBar": False}),
            html.Div(id="patho-advice-radar")
        ]),
    ]),

    # Ligne 3
    html.Div(className="charts-grid", children=[
        html.Div(className="chart-card", children=[
            html.Div("💊 Traitement par pathologie", className="chart-title"),
            html.Div("Répartition des traitements pour chaque maladie", className="chart-subtitle"),
            dcc.Graph(id="patho-bar-traitement", config={"displayModeBar": False}),
            html.Div(id="patho-advice-bar-traitement")
        ]),
        html.Div(className="chart-card", children=[
            html.Div("💉 Efficience thérapeutique", className="chart-title"),
            html.Div("Coût moyen par traitement — aide au choix thérapeutique", className="chart-subtitle"),
            dcc.Graph(id="patho-donut-traitement", config={"displayModeBar": False}),
            html.Div(id="patho-advice-donut")
        ]),
    ]),
])


@callback(
    Output("patho-kpis", "children"),
    Output("patho-insight", "children"),
    Output("patho-treemap", "figure"),
    Output("patho-sunburst", "figure"),
    Output("patho-heatmap", "figure"),
    Output("patho-radar", "figure"),
    Output("patho-bar-traitement", "figure"),
    Output("patho-donut-traitement", "figure"),
    Output("patho-advice-treemap", "children"),
    Output("patho-advice-sunburst", "children"),
    Output("patho-advice-heatmap", "children"),
    Output("patho-advice-radar", "children"),
    Output("patho-advice-bar-traitement", "children"),
    Output("patho-advice-donut", "children"),
    *FILTER_INPUTS,
)
def update_pathologies(dept, maladie, sexe, age, traitement, date_start, date_end):
    filters = build_filters_dict(
        dept, maladie, sexe, age, traitement, date_start, date_end
    )
    df = load_data()
    df = apply_filters(df, filters)

    import plotly.graph_objects as go
    if len(df) == 0:
        empty = go.Figure().update_layout(**PLOTLY_LAYOUT)
        empty_adv = html.Div()
        return [], html.Div(), empty, empty, empty, empty, empty, empty, empty_adv, empty_adv, empty_adv, empty_adv, empty_adv, empty_adv

    mal_stats = stats_par_maladie(df)
    trait_stats = stats_par_traitement(df)

    # ── KPIs ──
    top_mal = mal_stats.iloc[0] if len(mal_stats) > 0 else {}
    n_maladies = df["Maladie"].nunique()
    n_traitements = df["Traitement"].nunique()
    mal_plus_longue = df.groupby("Maladie")["DureeSejour"].mean().idxmax() if len(df) > 0 else "N/A"
    dms_max = df.groupby("Maladie")["DureeSejour"].mean().max()

    kpis = [
        kpi_card("Pathologies", str(n_maladies), "🩺", "#F87171",
                 f"Top coût : {top_mal.get('Maladie', 'N/A')}"),
        kpi_card("Traitements", str(n_traitements), "💊", "#34D399",
                 f"{len(df)} séjours analysés"),
        kpi_card("Prévalence max", f"{top_mal.get('Prevalence', 0):.1f}%",
                 "📊", "#FBBF24",
                 f"{top_mal.get('Maladie', 'N/A')} : {top_mal.get('Patients', 0)} cas"),
        kpi_card("DMS max", f"{dms_max:.1f} j", "⏱️", "#A78BFA",
                 f"{mal_plus_longue}"),
    ]

    # ── Insight ──
    if len(mal_stats) >= 2:
        most_expensive = mal_stats.loc[mal_stats["CoutMoyen"].idxmax()]
        least_expensive = mal_stats.loc[mal_stats["CoutMoyen"].idxmin()]
        ecart = most_expensive["CoutMoyen"] - least_expensive["CoutMoyen"]
        insight = html.Div(className="insight-box warning", children=[
            html.Div("🩺 Évaluation Clinique & Recommandations", className="insight-title"),
            html.Div(
                f"👉 Diagnostic Stratégique : La disparité des coûts est majeure. Le traitement de la pathologie '{most_expensive['Maladie']}' exige en moyenne {most_expensive['CoutMoyen']:,.0f} €, créant un différentiel brut de {ecart:,.0f} € face à des pathologies moins lourdes (" + least_expensive['Maladie'] + ").",
                className="insight-text", style={"marginBottom": "8px"}
            ),
            html.Div(
                f"👉 Explication : Cette forte intensité financière concentrée implique potentiellement la commande de machineries lourdes de traitement (réanimation, interventionnel) ou des schémas médicamenteux ciblés extrêmement onéreux.",
                 className="insight-text", style={"marginBottom": "8px"}
            ),
             html.Div(
                "💡 Actions recommandées : Lancer des revues de protocoles cliniques (Audit de prescription) via les Chefs de Pôle pour le traitement de '"+ most_expensive['Maladie'] +"'. Vérifiez si un passage partiel en filière ambulatoire est sanitairement sécurisé.",
                className="insight-text", style={"fontWeight": "500", "color": "#FBBF24"}
            )
        ])
    else:
        insight = html.Div()

    # ── Treemap ──
    tree_data = df.groupby(["Departement", "Maladie"]).size().reset_index(name="Patients")
    fig_tree = treemap_chart(tree_data, path=["Departement", "Maladie"],
                              values="Patients", title="",
                              color_map=DEPT_COLORS)
    fig_tree.update_layout(height=420)

    # ── Sunburst ──
    sun_data = df.groupby(["Departement", "Maladie", "Traitement"]).size().reset_index(name="Patients")
    fig_sun = sunburst_chart(sun_data, path=["Departement", "Maladie", "Traitement"],
                              values="Patients", title="",
                              color_map=DEPT_COLORS)
    fig_sun.update_layout(height=420)

    # ── Heatmap coût moyen ──
    matrix = matrice_maladie_departement(df, valeur="mean_cost")
    fig_heat = heatmap(matrix, title="", colorscale="YlOrRd")
    fig_heat.update_layout(height=400)

    # ── Radar ──
    if len(mal_stats) > 0:
        radar_cats = mal_stats["Maladie"].tolist()
        # Normaliser chaque métrique 0-100 pour le radar
        cout_norm = (mal_stats["CoutMoyen"] / mal_stats["CoutMoyen"].max() * 100).tolist()
        dms_norm = (mal_stats["DMS"] / mal_stats["DMS"].max() * 100).tolist()
        prev_norm = (mal_stats["Prevalence"] / mal_stats["Prevalence"].max() * 100).tolist()
        # Score composite moyen
        scores = [(c + d + p) / 3 for c, d, p in zip(cout_norm, dms_norm, prev_norm)]
        fig_radar = radar_chart(radar_cats, scores, title="", color="#0AEFB7")
    else:
        fig_radar = go.Figure().update_layout(**PLOTLY_LAYOUT)
    fig_radar.update_layout(height=400)

    # ── Bar traitement × maladie ──
    trait_mal = df.groupby(["Maladie", "Traitement"]).size().reset_index(name="Patients")
    fig_bar_trait = bar_grouped(trait_mal, "Maladie", "Patients",
                                 color="Traitement", title="",
                                 color_map=TRAITEMENT_COLORS, barmode="stack")
    fig_bar_trait.update_layout(height=400)

    # ── Donut traitement coûts ──
    trait_counts = df["Traitement"].value_counts()
    fig_donut_trait = donut_chart(
        trait_counts.index.tolist(),
        trait_counts.values.tolist(),
        title="",
        colors=[TRAITEMENT_COLORS.get(t, "#14919B") for t in trait_counts.index],
    )
    fig_donut_trait.update_layout(height=400)

    # -- EXPERT ADVICES DYNAMICS --
    if len(tree_data) > 0:
        top_combo_tree = tree_data.loc[tree_data["Patients"].idxmax()]
        adv_treemap = html.Div([
            html.Strong("💡 Interprétation : "), f"Le couplage ['{top_combo_tree['Departement']} - {top_combo_tree['Maladie']}'] occupe l'écrasante majorité de vos ressources physiques. ",
            html.Strong("Action : "), f"Garantissez le staffing médical exclusif sur la filière '{top_combo_tree['Maladie']}' au sein de '{top_combo_tree['Departement']}'."
        ], className="chart-expert-advice")
    else: adv_treemap = html.Div()

    if len(sun_data) > 0:
        top_sun = sun_data.loc[sun_data["Patients"].idxmax()]
        adv_sunburst = html.Div([
            html.Strong("💡 Interprétation : "), f"La chaîne de parcours la plus standardisée s'arrête sur le traitement '{top_sun['Traitement']}'. ",
            html.Strong("Action : "), f"Assurez des stocks logistiques suffisants (Pharmacie / DM) pour '{top_sun['Traitement']}' limitant ainsi toute rupture d'activité."
        ], className="chart-expert-advice")
    else: adv_sunburst = html.Div()

    if len(df) > 0:
        med_cost_dept_mal = df.groupby(["Departement", "Maladie"])["Cout"].mean().reset_index()
        top_heat = med_cost_dept_mal.loc[med_cost_dept_mal["Cout"].idxmax()]
        adv_heatmap = html.Div([
            html.Strong("💡 Interprétation : "), f"La zone de tension financière maximale se situe sur le couple '{top_heat['Departement']}' / '{top_heat['Maladie']}' ({top_heat['Cout']:,.0f} € moy.). ",
            html.Strong("Action : "), f"Une intervention ciblée du DIM (Département d'Information Médicale) est requise pour certifier le codage CCAM de cette activité coûteuse."
        ], className="chart-expert-advice")
    else: adv_heatmap = html.Div()

    if len(mal_stats) > 0:
        # Re-calc score composite to find max
        cout_norm = mal_stats["CoutMoyen"] / mal_stats["CoutMoyen"].max() * 100
        dms_norm = mal_stats["DMS"] / mal_stats["DMS"].max() * 100
        prev_norm = mal_stats["Prevalence"] / mal_stats["Prevalence"].max() * 100
        scores_s = (cout_norm + dms_norm + prev_norm) / 3
        top_radar = mal_stats.iloc[scores_s.idxmax()]["Maladie"]
        adv_radar = html.Div([
            html.Strong("💡 Interprétation : "), f"La pathologie '{top_radar}' cumule les pires scores de votre typologie (coût, temps, volume). ",
            html.Strong("Action : "), f"Ce « Case-Mix » dangereux impose une révision clinique immédiate des protocoles entourant '{top_radar}'."
        ], className="chart-expert-advice")
    else: adv_radar = html.Div()

    if len(trait_mal) > 0:
        adv_bar_trait = html.Div([
            html.Strong("💡 Interprétation : "), "Une variabilité de traitements au sein d'une même maladie dénote soit de cas complexes, soit d'un manque de standardisation. ",
            html.Strong("Action : "), "Demandez au Collège Médical de systématiser les prescriptions vers des GHM (Groupes Homogènes de Malades) plus prévisibles."
        ], className="chart-expert-advice")
    else: adv_bar_trait = html.Div()

    if len(trait_counts) > 0:
        top_trt = trait_counts.idxmax()
        adv_donut = html.Div([
            html.Strong("💡 Interprétation : "), f"Le type '{top_trt}' vampirise vos budgets d'actes en volume absolu. ",
            html.Strong("Action : "), f"Négociez des contrats-cadres ou des remises tarifaires sur les produits et dispositifs nécessaires à '{top_trt}'."
        ], className="chart-expert-advice")
    else: adv_donut = html.Div()

    return kpis, insight, fig_tree, fig_sun, fig_heat, fig_radar, fig_bar_trait, fig_donut_trait, adv_treemap, adv_sunburst, adv_heatmap, adv_radar, adv_bar_trait, adv_donut
