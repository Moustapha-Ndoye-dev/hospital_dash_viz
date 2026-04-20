import io
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, HRFlowable
)

# --- COULEURS ET CHARTE ---
BLEU_MEDICAL = colors.HexColor("#0F4C81")  # Classic Blue (Institutional)
BLEU_CLAIR = colors.HexColor("#3282B8")
GRIS_FONCE = colors.HexColor("#1B262C")
GRIS_CLAIR = colors.HexColor("#F7F9FC")
BLANC = colors.white

def generer_rapport_pdf(kpis: dict, stats_dept: list, stats_maladie: list, 
                       stats_traitement: list, filtres_actifs: str, 
                       narrative: dict = None):
    """
    Génère un rapport d'audit stratégique complet (Multi-pages, Expert).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=2.5*cm, leftMargin=2.5*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm
    )

    styles = getSampleStyleSheet()
    
    # Styles personnalisés pour l'audit prestige
    styles.add(ParagraphStyle(
        name="TitreAudit",
        parent=styles["Heading1"],
        fontSize=26,
        textColor=BLEU_MEDICAL,
        alignment=TA_CENTER,
        spaceAfter=30,
        fontName="Helvetica-Bold",
        leading=32
    ))

    styles.add(ParagraphStyle(
        name="SectionAudit",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=BLEU_MEDICAL,
        spaceBefore=25,
        spaceAfter=12,
        fontName="Helvetica-Bold",
        textTransform='uppercase',
        letterSpacing=1
    ))

    styles.add(ParagraphStyle(
        name="AuditText",
        parent=styles["Normal"],
        fontSize=10.5,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        textColor=GRIS_FONCE
    ))

    styles.add(ParagraphStyle(
        name="SignatureRole",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica-Bold",
        alignment=TA_RIGHT,
        spaceBefore=40
    ))

    styles.add(ParagraphStyle(
        name="SignatureName",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica-Oblique",
        alignment=TA_RIGHT,
        textColor=colors.grey
    ))

    elements = []

    # ═══════════════════════════════════
    # EN-TÊTE INSTITUTIONNEL
    # ═══════════════════════════════════
    elements.append(Paragraph("CENTRE HOSPITALIER UNIVERSITAIRE — DIRECTION GENERALE", styles["Normal"]))
    elements.append(Paragraph("POLE AUDIT ET CONTROLE DE GESTION", styles["Normal"]))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceBefore=5, spaceAfter=25))
    
    elements.append(Paragraph("RAPPORT COMPLET D'AUDIT MEDICO-ECONOMIQUE", styles["TitreAudit"]))
    
    elements.append(Paragraph(
        f"<b>Reference :</b> AUDIT-STRAT-{datetime.now().strftime('%Y%m')}-001<br/>"
        f"<b>Date d'emission :</b> {datetime.now().strftime('%d/%m/%Y')}<br/>"
        f"<b>Perimetre d'analyse :</b> {filtres_actifs}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 1.5 * cm))

    # ═══════════════════════════════════
    # CORPS DU RAPPORT (NARRATION LONGUE)
    # ═══════════════════════════════════
    if narrative:
        # I. Introduction
        elements.append(Paragraph("I. INTRODUCTION ET CADRE METHODOLOGIQUE", styles["SectionAudit"]))
        for p in narrative["intro"]:
            elements.append(Paragraph(p, styles["AuditText"]))

        # II. Activité
        elements.append(Paragraph("II. AUDIT DE L'EFFICIENCE ET DES PARCOURS PATIENTS", styles["SectionAudit"]))
        for p in narrative["activite"]:
            elements.append(Paragraph(p, styles["AuditText"]))

        # III. Finance
        elements.append(Paragraph("III. ANALYSE DE LA PERFORMANCE FINANCIERE ET T2A", styles["SectionAudit"]))
        for p in narrative["finance"]:
            elements.append(Paragraph(p, styles["AuditText"]))

        # IV. Spécialités
        elements.append(Paragraph("IV. DIAGNOSTIC DES FILIERES ET FOCUS CLINIQUE", styles["SectionAudit"]))
        for p in narrative["patho"]:
            elements.append(Paragraph(p, styles["AuditText"]))

        # V. Recommandations
        elements.append(Paragraph("V. RECOMMANDATIONS ET AXES STRATEGIQUES", styles["SectionAudit"]))
        for rec in narrative["recommandations"]:
            elements.append(Paragraph(f"• {rec}", styles["AuditText"]))

    # ═══════════════════════════════════
    # SIGNATURE ET VALIDEX
    # ═══════════════════════════════════
    elements.append(Spacer(1, 2 * cm))
    elements.append(Paragraph("Pour la Direction de l'Audit et du Pilotage,", styles["SignatureRole"]))
    elements.append(Paragraph("Moustapha Ndoye — Expert Consultant", styles["SignatureName"]))
    elements.append(Paragraph("Fait a Dakar, le " + datetime.now().strftime('%d/%m/%Y'), styles["SignatureName"]))

    # Note de bas de page (confidentiel)
    elements.append(Spacer(1, 3 * cm))
    elements.append(HRFlowable(width="30%", thickness=0.5, color=colors.lightgrey, hAlign="LEFT"))
    elements.append(Paragraph(
        "Ce document contient des informations strategiques soumises au secret professionnel. Toute reproduction externe est interdite sans accord prealable de la Direction Generale.",
        ParagraphStyle(name="Footer", parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    ))

    doc.build(elements)
    return buffer
