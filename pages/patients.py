"""
Page Patients — Analyse démographique.
Route : /patients
"""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.express as px
from utils.data_loader import load_data, apply_filters
from utils.filter_inputs import FILTER_INPUTS, build_filters_dict
from components.charts import (
    histogram, box_plot, donut_chart, scatter_plot, bar_grouped,
)
from components.kpi_card import kpi_card
from config import DEPT_COLORS, CHART_PALETTE, PLOTLY_LAYOUT

dash.register_page(__name__, path="/patients", name="Patients", title="Patients | Dashboard Hospitalier")

layout = html.Div([
    html.Div(className="page-header", children=[
        html.H1("👥 Analyse Démographique", className="page-title"),
        html.P("Profil des patients par âge, sexe et département", className="page-subtitle"),
    ]),

    # KPIs démographiques
    html.Div(id="patients-kpis", className="kpi-grid"),

    # Insight
    html.Div(id="patients-insight"),

    # Ligne 1
    html.Div(className="charts-grid", children=[
        html.Div(className="chart-card", children=[
            html.Div("📊 Distribution des âges", className="chart-title"),
            html.Div("Répartition de la population par âge", className="chart-subtitle"),
            dcc.Graph(id="patients-hist-age", config={"displayModeBar": False}),
            html.Div(id="patients-advice-age")
        ]),
        html.Div(className="chart-card", children=[
            html.Div("🎂 Répartition par tranche d'âge", className="chart-title"),
            html.Div("Catégories médicales standard", className="chart-subtitle"),
            dcc.Graph(id="patients-donut-tranche", config={"displayModeBar": False}),
            html.Div(id="patients-advice-tranche")
        ]),
    ]),

    # Ligne 2
    html.Div(className="charts-grid", children=[
        html.Div(className="chart-card", children=[
            html.Div("🏥 Âge par département", className="chart-title"),
            html.Div("Dispersion et médiane par service", className="chart-subtitle"),
            dcc.Graph(id="patients-box-age-dept", config={"displayModeBar": False}),
            html.Div(id="patients-advice-dept")
        ]),
        html.Div(className="chart-card", children=[
            html.Div("👤 Sexe par département", className="chart-title"),
            html.Div("Répartition hommes/femmes par service", className="chart-subtitle"),
            dcc.Graph(id="patients-bar-sexe-dept", config={"displayModeBar": False}),
            html.Div(id="patients-advice-sexe-dept")
        ]),
    ]),

    # Ligne 3
    html.Div(className="charts-grid", children=[
        html.Div(className="chart-card", children=[
            html.Div("💰 Âge vs Coût", className="chart-title"),
            html.Div("Corrélation entre l'âge du patient et le coût total", className="chart-subtitle"),
            dcc.Graph(id="patients-scatter-age-cout", config={"displayModeBar": False}),
            html.Div(id="patients-advice-scatter")
        ]),
        html.Div(className="chart-card", children=[
            html.Div("🩺 Âge moyen par pathologie", className="chart-title"),
            html.Div("Profil d'âge typique pour chaque maladie", className="chart-subtitle"),
            dcc.Graph(id="patients-bar-age-maladie", config={"displayModeBar": False}),
            html.Div(id="patients-advice-maladie")
        ]),
    ]),
])


@callback(
    Output("patients-kpis", "children"),
    Output("patients-insight", "children"),
    Output("patients-hist-age", "figure"),
    Output("patients-donut-tranche", "figure"),
    Output("patients-box-age-dept", "figure"),
    Output("patients-bar-sexe-dept", "figure"),
    Output("patients-scatter-age-cout", "figure"),
    Output("patients-bar-age-maladie", "figure"),
    Output("patients-advice-age", "children"),
    Output("patients-advice-tranche", "children"),
    Output("patients-advice-dept", "children"),
    Output("patients-advice-sexe-dept", "children"),
    Output("patients-advice-scatter", "children"),
    Output("patients-advice-maladie", "children"),
    *FILTER_INPUTS,
)
def update_patients(dept, maladie, sexe, age, traitement, date_start, date_end):
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

    # ── KPIs ──
    n_h = (df["Sexe"] == "M").sum()
    n_f = (df["Sexe"] == "F").sum()
    n_ped = (df["TrancheAge"] == "Pédiatrique (0-17)").sum()
    n_ger = (df["TrancheAge"] == "Gériatrique (65+)").sum()

    kpis = [
        kpi_card("Âge moyen", f"{df['Age'].mean():.1f} ans", "🎂", "#0AEFB7",
                 f"Médiane : {df['Age'].median():.0f} ans"),
        kpi_card("Hommes", f"{n_h}", "♂️", "#38BDF8",
                 f"{n_h / len(df) * 100:.1f}% de la cohorte"),
        kpi_card("Femmes", f"{n_f}", "♀️", "#F472B6",
                 f"{n_f / len(df) * 100:.1f}% de la cohorte"),
        kpi_card("Pédiatriques", f"{n_ped}", "👶", "#FBBF24",
                 f"{n_ped / len(df) * 100:.1f}% des patients"),
        kpi_card("Gériatriques", f"{n_ger}", "🧓", "#A78BFA",
                 f"{n_ger / len(df) * 100:.1f}% des patients"),
    ]

    # ── Insight ──
    idx_max_cost = df.groupby("TrancheAge")["Cout"].mean()
    tranche_max = idx_max_cost.idxmax()
    insight = html.Div(className="insight-box", children=[
        html.Div("🩺 Diagnostic Démographique & Orientations", className="insight-title"),
        html.Div(f"👉 État des lieux : Le profil patient générant le plus de coûts appartient à la classe d'âge « {tranche_max} » (Moyenne : {idx_max_cost.max():,.0f} €/séjour).", className="insight-text", style={"marginBottom": "8px"}),
        html.Div(f"👉 Explication clinique : Étonnamment, vieillir n'augmente pas conjointement la facture hospitalière (corrélation globale âge-coût : r={df['Age'].corr(df['Cout']):.2f}). Le véritable déclencheur budgétaire est la sévérité initiale et la durée d'alitement prolongée associée à la maladie.", className="insight-text", style={"marginBottom": "8px"}),
        html.Div(f"💡 Actions recommandées : Anticiper le plan de sortie des patients de la filière « {tranche_max} » dès leur admission (Staff Gériatrique/PRADO/SSIAD). Intervenir tôt sécurise la sortie et optimise la rotation des lits.", className="insight-text", style={"fontWeight": "500", "color": "#0AEFB7"})
    ])

    # ── Histogramme âge ──
    fig_hist = histogram(df, "Age", nbins=18, title="", color="#14919B")
    fig_hist.update_layout(height=350, xaxis_title="Âge", yaxis_title="Nombre de patients")

    # ── Donut tranche d'âge ──
    tranche_counts = df["TrancheAge"].value_counts()
    fig_donut = donut_chart(
        tranche_counts.index.tolist(),
        tranche_counts.values.tolist(),
        title="",
        colors=["#FBBF24", "#0AEFB7", "#A78BFA"],
    )
    fig_donut.update_layout(height=350)

    # ── Boxplot âge par département ──
    fig_box = box_plot(df, "Departement", "Age", title="", color_map=DEPT_COLORS)
    fig_box.update_layout(height=350, xaxis_title="", yaxis_title="Âge")

    # ── Stacked bar sexe × département ──
    sexe_dept = df.groupby(["Departement", "Sexe"]).size().reset_index(name="Patients")
    fig_sexe = bar_grouped(sexe_dept, "Departement", "Patients",
                           color="Sexe", title="",
                           color_map={"M": "#38BDF8", "F": "#F472B6"},
                           barmode="stack")
    fig_sexe.update_layout(height=350)

    # ── Scatter âge vs coût ──
    fig_scatter = scatter_plot(df, "Age", "Cout", color="Sexe", title="",
                               color_map={"M": "#38BDF8", "F": "#F472B6"},
                               trendline="ols")
    fig_scatter.update_layout(height=350, xaxis_title="Âge", yaxis_title="Coût (€)")

    # ── Bar âge moyen par maladie ──
    age_mal = df.groupby("Maladie")["Age"].mean().round(1).reset_index()
    age_mal.columns = ["Maladie", "AgeMoyen"]
    age_mal = age_mal.sort_values("AgeMoyen", ascending=True)
    fig_age_mal = px.bar(age_mal, x="AgeMoyen", y="Maladie", orientation="h",
                          color="Maladie",
                          color_discrete_sequence=CHART_PALETTE)
    fig_age_mal.update_traces(marker_line_width=0,
                               texttemplate="%{x:.1f}", textposition="outside",
                               textfont=dict(size=10, color="#7B8FA3"))
    fig_age_mal.update_layout(**PLOTLY_LAYOUT, height=350, showlegend=False,
                               xaxis_title="Âge moyen", yaxis_title="")

    # -- EXPERT ADVICES DYNAMICS --
    if len(df) > 0:
        age_mode = df["Age"].mode().max() # in case of multiple modes
        adv_age = html.Div([
            html.Strong("💡 Interprétation : "), f"Le public hospitalisé se concentre fortement autour de {int(age_mode)} ans. ",
            html.Strong("Action : "), f"Assurez-vous que l'ergonomie des lits et les repas proposés correspondent aux standards de la cohorte {int(age_mode)} ans."
        ], className="chart-expert-advice")
    else: adv_age = html.Div()
    
    if len(tranche_counts) > 0:
        top_t = tranche_counts.idxmax()
        adv_tranche = html.Div([
            html.Strong("💡 Interprétation : "), f"Le profil '{top_t}' domine ouvertement l'activité. ",
            html.Strong("Action : "), f"Adaptez vos partenariats extérieurs (associations d'aide ou EHPAD) au traitement de masse de la population '{top_t}'."
        ], className="chart-expert-advice")
    else: adv_tranche = html.Div()

    if len(df) > 0:
        med_dept = df.groupby("Departement")["Age"].median()
        vieux_dept = med_dept.idxmax()
        adv_dept = html.Div([
            html.Strong("💡 Interprétation : "), f"Le département '{vieux_dept}' traite les patients structurellement les plus âgés. ",
            html.Strong("Action : "), f"Affectez vos kinésithérapeutes prioritairement en '{vieux_dept}' pour lutter contre la perte d'autonomie liée à l'alitement."
        ], className="chart-expert-advice")
    else: adv_dept = html.Div()
    
    if len(sexe_dept) > 0:
        # Trouver le dept avec la plus grosse asymétrie
        dept_diffs = []
        for d in sexe_dept["Departement"].unique():
            sd = sexe_dept[sexe_dept["Departement"] == d]
            m = sd[sd["Sexe"] == "M"]["Patients"].sum()
            f = sd[sd["Sexe"] == "F"]["Patients"].sum()
            tot = m + f
            if tot > 0:
                diff = abs((m / tot) - (f / tot))
                dept_diffs.append((d, diff, "M" if m>f else "F"))
        dept_diffs.sort(key=lambda x: x[1], reverse=True)
        if dept_diffs:
            top_sd, top_diff, top_sexe = dept_diffs[0]
            adv_sexe_dept = html.Div([
                html.Strong("💡 Interprétation : "), f"'{top_sd}' est très asymétrique (dominance à {((0.5+top_diff/2)*100):.0f}% de {'Hommes' if top_sexe=='M' else 'Femmes'}). ",
                html.Strong("Action : "), f"Les chambres doubles de '{top_sd}' doivent logistiquement respecter cette distribution genrée stricte."
            ], className="chart-expert-advice")
        else:
            adv_sexe_dept = html.Div()
    else: adv_sexe_dept = html.Div()
        
    if len(df) > 0:
        corr_val = df["Age"].corr(df["Cout"])
        adv_scatter = html.Div([
            html.Strong("💡 Interprétation : "), f"La corrélation (r = {corr_val:.2f}) démontre l'absence de lien strict Âge-Cout. ",
            html.Strong("Action : "), "Ne conditionnez jamais une décision budgétaire ou d'investissement technique uniquement sur la pyramide des âges."
        ], className="chart-expert-advice")
    else: adv_scatter = html.Div()
    
    if len(age_mal) > 0:
        jeune_mal = age_mal.iloc[0]["Maladie"]
        adv_maladie = html.Div([
            html.Strong("💡 Interprétation : "), f"La maladie '{jeune_mal}' a l'âge moyen d'incidence le plus précoce. ",
            html.Strong("Action : "), f"Vérifiez l'accompagnement social précoce (retournement de carrière professionnelle) pour les victimes de '{jeune_mal}'."
        ], className="chart-expert-advice")
    else: adv_maladie = html.Div()

    return kpis, insight, fig_hist, fig_donut, fig_box, fig_sexe, fig_scatter, fig_age_mal, adv_age, adv_tranche, adv_dept, adv_sexe_dept, adv_scatter, adv_maladie
