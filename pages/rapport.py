import dash
from dash import html, dcc, callback, Input, Output, State
import pandas as pd
import io
from datetime import datetime
from utils.data_loader import load_data
from utils.statistics import (
    compute_kpis, stats_par_departement, stats_par_maladie,
    stats_par_traitement
)
from utils.pdf_generator import generer_rapport_pdf
from config import COLORS

dash.register_page(__name__, path='/rapport', name="📄 Rapport", order=6)

def kpi_card(title, value, emoji, color):
    """Carte KPI stylisée pour l'en-tête du rapport preview."""
    return html.Div(className="kpi-card", children=[
        html.Div(emoji, className="kpi-emoji", style={"backgroundColor": color + "1A", "color": color}),
        html.Div([
            html.Div(title, className="kpi-title"),
            html.Div(value, className="kpi-value"),
        ])
    ])

layout = html.Div(className="audit-container", children=[
    html.Div(className="page-header rapport-page-header", children=[
        html.Div(className="rapport-page-header-main", children=[
            html.H1("Direction de l'Audit Stratégique", className="page-title"),
            html.P("Rapports d'expertise médico-économique et pilotage institutionnel", className="page-subtitle"),
        ]),
        html.Div(className="rapport-actions-toolbar", children=[
            html.Button(
                [
                    html.I(className="fas fa-file-pdf"),
                    html.Span("Télécharger PDF", className="btn-label"),
                ],
                id="btn-download-pdf",
                className="btn-download pdf rapport-btn-icon",
                title="Exporter le rapport au format PDF",
                type="button",
            ),
            dcc.Download(id="download-pdf"),
        ]),
    ]),

    # Conteneur de l'aperçu du rapport (Paper View)
    html.Div(id="rapport-preview-container")
])

@callback(
    Output("rapport-preview-container", "children"),
    Input("filter-store", "data")
)
def update_rapport_preview(filters):
    df = load_data()
    df = apply_filters(df, filters)
    
    # Sécurité : Si aucune donnée ne correspond aux filtres
    if len(df) == 0:
        return html.Div(className="insight-box danger", children=[
            html.Div("⚠️ AUCUNE DONNÉE TROUVÉE", className="insight-title"),
            html.Div("Veuillez ajuster vos filtres car aucune admission ne correspond à ces critères.", className="insight-text"),
        ])

    kpis = compute_kpis(df)
    dept_stats = stats_par_departement(df)
    mal_stats = stats_par_maladie(df)
    
    # Génération du rapport narratif complet (Texte long, structuré)
    try:
        narrative = _generate_strategic_narrative(df, kpis, dept_stats, mal_stats)
    except Exception as e:
        return html.Div(f"Erreur lors de la génération du narratif : {str(e)}", style={"color": "red"})

    # Description des filtres actifs
    filtres_desc = _describe_filters(filters)
    ref_rapport = f"AUDIT-STRAT-{datetime.now().strftime('%Y%m')}-001"
    gen_time = datetime.now().strftime("%d/%m/%Y à %H:%M")

    return html.Div(className="audit-paper", children=[
        # --- EN-TÊTE INSTITUTIONNEL ---
        html.Div(className="audit-header", children=[
            html.Div("🏥 CENTRE HOSPITALIER UNIVERSITAIRE — DIRECTION GÉNÉRALE", className="institution-name"),
            html.H1("RAPPORT RÉCAPITULATIF D'AUDIT MÉDICO-ÉCONOMIQUE", className="report-title"),
            html.Div(f"SÉLECTION ANALYTIQUE : {filtres_desc}", style={"fontSize": "11px", "color": "#718096", "letterSpacing": "1px"}),
        ]),

        # --- SECTION NARRATIVE (Texte seul, bien paragraphé) ---
        
        # Introduction
        html.Div(className="audit-section", children=[
            html.Div([
                html.Span("I.", className="audit-section-number"),
                html.Span("INTRODUCTION ET CADRE MÉTHODOLOGIQUE", className="audit-section-title")
            ]),
            html.Div([html.P(p, className="audit-body-text") for p in narrative["intro"]]),
        ]),

        # Flux et DMS
        html.Div(className="audit-section", children=[
            html.Div([
                html.Span("II.", className="audit-section-number"),
                html.Span("AUDIT DE L'EFFICIENCE ET DES PARCOURS", className="audit-section-title")
            ]),
            html.Div([html.P(p, className="audit-body-text") for p in narrative["activite"]]),
        ]),

        # Finance
        html.Div(className="audit-section", children=[
            html.Div([
                html.Span("III.", className="audit-section-number"),
                html.Span("PILOTAGE BUDGÉTAIRE ET ANALYSE T2A", className="audit-section-title")
            ]),
            html.Div([html.P(p, className="audit-body-text") for p in narrative["finance"]]),
        ]),

        # Spécialités
        html.Div(className="audit-section", children=[
            html.Div([
                html.Span("IV.", className="audit-section-number"),
                html.Span("DIAGNOSTIC DES FILIÈRES ET FOCUS CLINIQUE", className="audit-section-title")
            ]),
            html.Div([html.P(p, className="audit-body-text") for p in narrative["patho"]]),
        ]),

        # --- SECTION : RECOMMANDATIONS ---
        html.Div(className="audit-recommendation-box", children=[
            html.Div(className="audit-recommendation-title", children=[
                html.I(className="fas fa-bullseye"),
                "AXES D'AMÉLIORATION ET RECOMMANDATIONS STRATÉGIQUES"
            ]),
            html.Ul(children=[
                html.Li(r, style={"marginBottom": "12px", "fontSize": "14.5px", "color": "#2D3748", "textAlign": "justify"}) 
                for r in narrative["recommandations"]
            ])
        ]),

        # --- BLOC DE SIGNATURE ---
        html.Div(className="audit-signature-block", children=[
            html.Div("Le Directeur de l'Audit et du Pilotage", className="audit-signature-role"),
            html.Div("Moustapha Ndoye — Expert Consultant", className="audit-signature-name"),
            html.Div("VALIDE", className="audit-stamp")
        ]),

        # PIED DE PAGE
        html.Div(className="audit-footer", children=[
            html.P("Document confidentiel · Diffusion restreinte · Direction Générale du CHU"),
            html.P(f"Rapport d'expertise n°2025-AUD-{datetime.now().strftime('%m%d%H%M')}"),
        ])
    ])

@callback(
    Output("download-pdf", "data"),
    Input("btn-download-pdf", "n_clicks"),
    State("filter-store", "data"),
    prevent_initial_call=True,
)
def download_pdf(n_clicks, filters):
    df = load_data()
    df = apply_filters(df, filters)
    kpis = compute_kpis(df)
    dept_df = stats_par_departement(df)
    mal_df = stats_par_maladie(df)
    trait_df = stats_par_traitement(df)
    filtres_desc = _describe_filters(filters)
    
    narrative = _generate_strategic_narrative(df, kpis, dept_df, mal_df)

    buffer = generer_rapport_pdf(
        kpis, dept_df.to_dict("records"), 
        mal_df.to_dict("records"), trait_df.to_dict("records"), 
        filtres_desc, narrative
    )

    return dcc.send_bytes(buffer.getvalue(), f"Audit_Strategique_{datetime.now().strftime('%Y%m%d')}.pdf")


# ── Fonctions utilitaires ──

def apply_filters(df, filters):
    if not filters: return df
    dff = df.copy()
    if filters.get("dept") and filters["dept"] != "Tous":
        dff = dff[dff["Departement"] == filters["dept"]]
    if filters.get("patho") and filters["patho"] != "Tous":
        dff = dff[dff["Maladie"] == filters["patho"]]
    if filters.get("sexe") and filters["sexe"] != "Tous":
        dff = dff[dff["Sexe"] == filters["sexe"]]
    if filters.get("age_range"):
        dff = dff[dff["TrancheAge"].isin(filters["age_range"])]
    if filters.get("treatment") and filters["treatment"] != "Tous":
        dff = dff[dff["Traitement"] == filters["treatment"]]
    if filters.get("date_start") and filters.get("date_end"):
        dff = dff[(dff["DateAdmission"] >= filters["date_start"]) & 
                    (dff["DateAdmission"] <= filters["date_end"])]
    return dff

def _describe_filters(filters):
    if not filters: return "Ensemble de l'activité"
    parts = []
    if filters.get("dept") and filters["dept"] != "Tous": parts.append(f"Pôle: {filters['dept']}")
    if filters.get("patho") and filters["patho"] != "Tous": parts.append(f"Patho: {filters['patho']}")
    if not parts: return "Cohorte complète"
    return " | ".join(parts)

def _format_value(val) -> str:
    if isinstance(val, (int, float)):
        if pd.isna(val): return "0"
        if val > 1000: return f"{val:,.0f}".replace(",", " ")
        return f"{val:.1f}"
    return str(val)

def _generate_strategic_narrative(df, kpis, dept_stats, mal_stats) -> dict:
    """Génère un rapport d'audit complet de plus d'une page."""
    
    worst_dept = dept_stats.iloc[0] if len(dept_stats) > 0 else {"Departement": "N/A", "DMS": 0}
    top_patho = mal_stats.iloc[0] if len(mal_stats) > 0 else {"Maladie": "N/A", "Patients": 0}
    
    # I. Introduction
    intro = [
        f"Le présent audit medico-économique porte sur une cohorte de {kpis['total_patients']} patients, enregistrée sur la base des données d'hospitalisation de l'établissement. Ce document s'inscrit dans la démarche de pilotage stratégique du CHU visant à garantir une adéquation optimale entre les ressources mobilisées et l'intensité de l'activité clinique constatée.",
        "La méthodologie d'audit repose sur une analyse croisée des indicateurs de durée de séjour (DMS) et des coûts directs par séjour. L'objectif est de mettre en lumière les éventuelles dérives du parcours de soin et d'identifier les poches d'efficience inexploités pour sécuriser la trajectoire budgétaire annuelle."
    ]
    
    # II. Activité et Flux
    activite = [
        f"L'analyse des flux révèle une Durée Moyenne de Séjour (DMS) stabilisée à {kpis['dms']} jours sur le périmètre sélectionné. Cependant, une hétérogénéité significative est observée entre les différents services. Le pôle '{worst_dept['Departement']}' présente notamment les indicateurs de tension les plus élevés avec une DMS moyenne de {worst_dept['DMS']} jours, ce qui impacte directement le taux de rotation des lits et crée des goulots d'étranglement capacitaires en amont, notamment aux urgences.",
        "Il est impératif d'étudier les causes racines de cet allongement des séjours : retard dans les bilans diagnostiques, difficultés d'évacuation vers les structures de soins de suite (SSR) ou complexité inhérente à la patientèle spécifique de ce département. Une réduction de 10% de cette DMS locale permettrait de libérer une capacité d'accueil substantielle sans investissement immobilier complémentaire."
    ]
    
    # III. Finance
    finance = [
        f"Sur le plan budgétaire, l'enveloppe cumulée des soins pour cette cohorte s'élève à {kpis['cout_total']:,.0f} EUR, pour un coût moyen par séjour de {kpis['cout_moyen']:,.0f} EUR. L'intensité de coût par journée d'hospitalisation, évaluée à {kpis['cout_par_jour']:,.0f} EUR/j, témoigne d'un niveau élevé de technicité des soins, mais expose également l'établissement à un risque de déficit si le codage T2A n'est pas optimisé.",
        f"Nous identifions actuellement {kpis['patients_critiques']} séjours dits 'critiques' dépassant les seuils de rentabilité par GHM (Groupes Homogènes de Malades). Ces cas isolés absorbent une part disproportionnée des ressources. Un audit ciblé du codage DIM sur ces dossiers est préconisé afin de s'assurer que la complexité médicale et les comorbidités associées sont exhaustivement capturées dans les résumés de sortie anonymisés (RSA)."
    ]
    
    # IV. Pathologie
    patho = [
        f"Le diagnostic des filières de spécialités met en évidence la prédominance de la pathologie '{top_patho['Maladie']}' qui concentre à elle seule {top_patho['Patients']} admissions. Cette filière constitue l'axe clinique majeur de la période analysée. Cependant, la variabilité des coûts au sein de cette même pathologie suggère des disparités dans l'application des protocoles thérapeutiques entre les différents praticiens.",
        "Une standardisation des parcours de soins pour les pathologies à haut volume permettrait not seulement de stabiliser les coûts, mais également de garantir une équité de prise en charge pour l'ensemble des patients. La mise en place de 'chemins cliniques' informatisés est recommandée pour réduire l'aléa médical et optimiser la consommation des ressources hôtelières et logistiques."
    ]
    
    recommandations = [
        f"Réalisation d'un audit de 'parcours patient' spécifique au département {worst_dept['Departement']} pour identifier les points de blocage post-opératoires ou diagnostiques.",
        "Renforcement de l'amont du codage (pré-DIM) pour les hospitalisations longues afin de maximiser la valorisation des points ISA/T2A.",
        f"Lancement d'un groupe de travail sur la standardisation des prescriptions pour la filière '{top_patho['Maladie']}' afin de réduire l'écart-type des dépenses pharmaceutiques.",
        "Intégration systématique d'un indicateur de 'coût réel vs tarif GHM' dans les tableaux de bord de pilotage des chefs de service."
    ]

    return {
        "intro": intro,
        "activite": activite,
        "finance": finance,
        "patho": patho,
        "recommandations": recommandations
    }
