from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import PageBreak

# ── Colour palette ─────────────────────────────────────────────────────────────
NAVY     = colors.HexColor("#0D1F3C")
TEAL     = colors.HexColor("#0A7EA4")
TEAL_LT  = colors.HexColor("#E6F4F9")
SLATE    = colors.HexColor("#4A5568")
SILVER   = colors.HexColor("#E2E8F0")
WHITE    = colors.white
AMBER    = colors.HexColor("#D97706")
GREEN    = colors.HexColor("#059669")

W, H = A4

# ── Document setup ─────────────────────────────────────────────────────────────
OUTPUT = r"C:\AI\projects\Podcast\AI_Voice_Studio_Briefing.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=2.2*cm,
    rightMargin=2.2*cm,
    topMargin=2*cm,
    bottomMargin=2*cm,
    title="AI Voice Studio — Executive Briefing",
    author="Internal — Confidential",
)

# ── Styles ─────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def style(name, **kw):
    base = styles["Normal"] if name not in styles else styles[name]
    return ParagraphStyle(name + "_custom", parent=base, **kw)

S = {
    "cover_title": style("Title",
        fontSize=32, textColor=WHITE, leading=40,
        alignment=TA_CENTER, fontName="Helvetica-Bold"),

    "cover_sub": style("Normal",
        fontSize=14, textColor=colors.HexColor("#A8D4E8"),
        alignment=TA_CENTER, spaceAfter=6),

    "cover_meta": style("Normal",
        fontSize=10, textColor=colors.HexColor("#7FB3C8"),
        alignment=TA_CENTER),

    "section_label": style("Normal",
        fontSize=9, textColor=TEAL, fontName="Helvetica-Bold",
        spaceBefore=18, spaceAfter=2, letterSpacing=1.5),

    "h1": style("Heading1",
        fontSize=18, textColor=NAVY, fontName="Helvetica-Bold",
        spaceAfter=6, spaceBefore=0),

    "h2": style("Heading2",
        fontSize=13, textColor=NAVY, fontName="Helvetica-Bold",
        spaceBefore=14, spaceAfter=4),

    "h3": style("Heading3",
        fontSize=11, textColor=TEAL, fontName="Helvetica-Bold",
        spaceBefore=10, spaceAfter=3),

    "body": style("Normal",
        fontSize=10, textColor=SLATE, leading=16,
        alignment=TA_JUSTIFY, spaceAfter=6),

    "bullet": style("Normal",
        fontSize=10, textColor=SLATE, leading=15,
        leftIndent=14, spaceAfter=3),

    "callout": style("Normal",
        fontSize=10, textColor=NAVY, leading=15,
        leftIndent=10, rightIndent=10, fontName="Helvetica-Oblique"),

    "table_hdr": style("Normal",
        fontSize=9, textColor=WHITE, fontName="Helvetica-Bold",
        alignment=TA_CENTER),

    "table_cell": style("Normal",
        fontSize=9, textColor=SLATE, leading=13),

    "table_cell_c": style("Normal",
        fontSize=9, textColor=SLATE, leading=13,
        alignment=TA_CENTER),

    "footer_label": style("Normal",
        fontSize=8, textColor=colors.HexColor("#94A3B8"),
        alignment=TA_CENTER),

    "tag": style("Normal",
        fontSize=8, textColor=WHITE, fontName="Helvetica-Bold",
        alignment=TA_CENTER),
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def P(text, s="body"): return Paragraph(text, S[s])
def SP(n=6):           return Spacer(1, n)
def HR(color=SILVER, thickness=0.5): return HRFlowable(width="100%", thickness=thickness, color=color)

def section_header(label, title):
    return [
        SP(4),
        P(label.upper(), "section_label"),
        P(title, "h1"),
        HR(TEAL, 1.5),
        SP(8),
    ]

def bullet(text, icon="•"):
    return P(f"<b>{icon}</b>  {text}", "bullet")

def callout_box(text, bg=TEAL_LT):
    tbl = Table([[P(text, "callout")]], colWidths=[W - 4.4*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("ROUNDEDCORNERS", [4]),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING",   (0,0), (-1,-1), 14),
        ("RIGHTPADDING",  (0,0), (-1,-1), 14),
        ("BOX", (0,0), (-1,-1), 1, TEAL),
    ]))
    return tbl


# ── Page templates (header/footer) ────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    page_num = doc.page

    # Top bar
    canvas.setFillColor(NAVY)
    canvas.rect(0, H - 1.1*cm, W, 1.1*cm, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0, H - 1.1*cm, 0.6*cm, 1.1*cm, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(WHITE)
    canvas.drawString(1*cm, H - 0.7*cm, "AI Voice Studio — Executive Briefing")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#7FB3C8"))
    canvas.drawRightString(W - 1*cm, H - 0.7*cm, "INTERNAL — CONFIDENTIAL")

    # Bottom bar
    canvas.setFillColor(SILVER)
    canvas.rect(0, 0, W, 0.8*cm, fill=1, stroke=0)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(SLATE)
    canvas.drawString(1*cm, 0.25*cm, f"Page {page_num}")
    canvas.drawCentredString(W/2, 0.25*cm, "Proprietary & Confidential — Not for external distribution")
    canvas.restoreState()


def on_cover(canvas, doc):
    canvas.saveState()
    # Full-page gradient background
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    # Teal accent strip
    canvas.setFillColor(TEAL)
    canvas.rect(0, 0, W, 0.6*cm, fill=1, stroke=0)
    canvas.rect(0, H - 0.6*cm, W, 0.6*cm, fill=1, stroke=0)
    # Decorative circle
    canvas.setFillColor(colors.HexColor("#112A4A"))
    canvas.circle(W - 3*cm, H - 5*cm, 5*cm, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#0A3558"))
    canvas.circle(W - 2*cm, H - 5.5*cm, 3*cm, fill=1, stroke=0)
    canvas.restoreState()


# ── Story ──────────────────────────────────────────────────────────────────────
story = []

# ─── COVER PAGE ───────────────────────────────────────────────────────────────
story.append(Spacer(1, 3.5*cm))
story.append(P("AI Voice Studio", "cover_title"))
story.append(SP(8))
story.append(P("A Privacy-First Voice Intelligence Platform", "cover_sub"))
story.append(P("for the Health Sector", "cover_sub"))
story.append(SP(28))

cover_meta = [
    ["Product Concept Briefing", "May 2025"],
    ["Classification:", "Internal — Confidential"],
    ["Audience:", "Internal Team"],
]
meta_tbl = Table(cover_meta, colWidths=[8*cm, 8*cm])
meta_tbl.setStyle(TableStyle([
    ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#7FB3C8")),
    ("FONTNAME",  (0,0), (0,-1), "Helvetica-Bold"),
    ("FONTSIZE",  (0,0), (-1,-1), 10),
    ("ALIGN",     (1,0), (1,-1), "RIGHT"),
    ("LINEABOVE", (0,0), (-1,0), 0.5, colors.HexColor("#1E3A5F")),
    ("LINEBELOW", (0,-1), (-1,-1), 0.5, colors.HexColor("#1E3A5F")),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
]))
story.append(meta_tbl)

story.append(PageBreak())


# ─── EXECUTIVE SUMMARY ────────────────────────────────────────────────────────
story += section_header("Overview", "Executive Summary")

story.append(P(
    "This briefing outlines a concept for a proprietary AI-powered voice content platform "
    "designed specifically for the health sector. The platform enables organisations to create "
    "professional-grade audio content — such as clinical briefings, patient education material, "
    "and staff communications — using personalised AI voice personas trained on real human voices.",
    "body"
))
story.append(SP(6))
story.append(P(
    "The core differentiator is a <b>privacy-first architecture</b>: all voice data, transcripts, "
    "and generated audio remain under the organisation's direct control, satisfying the requirements "
    "of the NZ Privacy Act 2020, the Health Information Privacy Code 2020, and Health New Zealand "
    "procurement standards.",
    "body"
))
story.append(SP(10))

story.append(callout_box(
    "<b>The opportunity:</b> Health organisations produce significant volumes of written content "
    "(clinical guidelines, patient communications, training material) that could reach staff and patients "
    "more effectively as on-demand audio. No compliant, affordable, local solution exists for this today."
))

story.append(SP(16))


# ─── THE PROBLEM ──────────────────────────────────────────────────────────────
story += section_header("The Problem", "Health Sector Content Has a Last-Mile Problem")

story.append(P(
    "Clinical teams produce enormous volumes of written content — guidelines, procedure updates, "
    "patient education, training material — that frequently goes unread. Audio is more accessible, "
    "more engaging, and more inclusive. Yet health organisations face a critical blocker:",
    "body"
))
story.append(SP(8))

problems = [
    ("Data sovereignty", "Health information cannot be processed by external cloud services without a documented risk assessment and patient/staff consent. Most commercial AI voice tools send data offshore."),
    ("Voice quality gap", "Free or open-source tools produce robotic, unconvincing audio that undermines professional credibility."),
    ("No personalisation", "Generic AI voices lack the authority and familiarity of a known clinician or trusted organisation voice."),
    ("Compliance overhead", "Building a compliant in-house solution has historically required specialist AI engineering expertise that health organisations do not have."),
]

for title, desc in problems:
    story.append(KeepTogether([
        P(f"<b>{title}</b>", "h3"),
        P(desc, "body"),
    ]))

story.append(SP(10))

story.append(PageBreak())


# ─── THE SOLUTION ─────────────────────────────────────────────────────────────
story += section_header("Solution", "What We Are Building")

story.append(P(
    "A self-contained, web-based platform that allows health organisations to:",
    "body"
))
story.append(SP(4))

capabilities = [
    ("Train a voice persona", "A clinician, presenter, or brand voice records a short audio sample. The platform learns that voice and stores it securely within the organisation's own infrastructure."),
    ("Generate audio from any transcript", "Staff paste or upload a written document. The platform rewrites it into natural, conversational spoken language and synthesises it in the chosen voice."),
    ("Choose the format", "Single narrator for briefings and education material, or a two-voice conversation format for more engaging content — similar to a professional podcast."),
    ("Manage voice libraries", "Organisations build a library of approved voices — both individual staff personas and official organisational voices — that can be used across the team."),
]

for i, (title, desc) in enumerate(capabilities):
    row = Table(
        [[P(str(i+1), "table_hdr"), P(f"<b>{title}</b><br/>{desc}", "body")]],
        colWidths=[1*cm, W - 4.4*cm - 1.2*cm]
    )
    row.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,0), TEAL),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (1,0), (1,0), 12),
    ]))
    story.append(KeepTogether([row, SP(6)]))

story.append(SP(10))


# ─── QUALITY & PREMIUM EXPERIENCE ─────────────────────────────────────────────
story += section_header("Quality", "Premium Audio — Not Robotic")

story.append(P(
    "The quality gap between consumer AI voice tools and professional broadcast audio has historically "
    "been a barrier to adoption. This platform closes that gap through a layered approach:",
    "body"
))
story.append(SP(6))

quality_points = [
    "Natural language rewriting — the system transforms written text into spoken language before synthesis, adding natural pacing, conversational rhythm, and appropriate emphasis",
    "Emotional intelligence — the audio engine interprets context to vary tone, warmth, and energy across the content rather than reading at a flat, uniform pace",
    "Broadcast-standard audio processing — the final output is professionally processed to match the loudness and clarity standards used in commercial radio and podcasting",
    "Voice consistency — trained personas sound consistent across any content, reinforcing organisational voice and brand",
]

for pt in quality_points:
    story.append(bullet(pt))
    story.append(SP(2))

story.append(SP(10))


# ─── PRIVACY & GOVERNANCE ─────────────────────────────────────────────────────
story += section_header("Privacy & Governance", "Built for NZ Health Compliance")

story.append(P(
    "Privacy is not an add-on — it is the architectural foundation. The platform is designed "
    "to meet the specific requirements of the NZ regulatory environment:",
    "body"
))
story.append(SP(8))

gov_data = [
    [P("Requirement", "table_hdr"), P("How it is addressed", "table_hdr")],
    [P("NZ Privacy Act 2020", "table_cell"), P("All personal data processed and stored within the organisation's own infrastructure", "table_cell")],
    [P("Health Information Privacy Code 2020", "table_cell"), P("Voice samples treated as sensitive biometric data — encrypted, access-logged, and deletable on request", "table_cell")],
    [P("Health NZ procurement standards", "table_cell"), P("Two deployment options available to match each organisation's risk appetite and infrastructure", "table_cell")],
    [P("Staff consent", "table_cell"), P("Built-in consent workflow — staff explicitly consent before any voice persona is created, with a logged timestamp", "table_cell")],
    [P("Audit trail", "table_cell"), P("Every action (who created what, when, using which voice) is logged in an immutable audit record", "table_cell")],
    [P("Access control", "table_cell"), P("Role-based permissions — org administrators, content creators, and viewers each have appropriate access levels", "table_cell")],
    [P("Data breach readiness", "table_cell"), P("Monitoring and alerting aligned with the 72-hour Privacy Commissioner notification requirement", "table_cell")],
]

gov_tbl = Table(gov_data, colWidths=[5.5*cm, W - 4.4*cm - 5.7*cm])
gov_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,0), NAVY),
    ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, TEAL_LT]),
    ("GRID",          (0,0), (-1,-1), 0.4, SILVER),
    ("TOPPADDING",    (0,0), (-1,-1), 7),
    ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ("RIGHTPADDING",  (0,0), (-1,-1), 8),
    ("VALIGN",        (0,0), (-1,-1), "TOP"),
]))
story.append(gov_tbl)

story.append(SP(10))

story.append(PageBreak())


# ─── TWO DEPLOYMENT OPTIONS ───────────────────────────────────────────────────
story += section_header("Deployment", "Two Options — One Decision")

story.append(P(
    "The platform is designed to work in either of two deployment modes, depending on the "
    "organisation's infrastructure and risk appetite. The same product, the same interface, "
    "the same quality — the difference is where the computation happens.",
    "body"
))
story.append(SP(10))

options_data = [
    [P("", "table_hdr"), P("Option A\nFully On-Premises", "table_hdr"), P("Option B\nManaged Cloud (NZ-Hosted)", "table_hdr")],
    [P("Where data lives", "table_cell_c"),   P("Inside the organisation's own server room — nothing leaves the building", "table_cell"), P("Within a New Zealand-based data centre, under a formal data processing agreement", "table_cell")],
    [P("Internet required", "table_cell_c"),  P("No — fully air-gapped capable", "table_cell"), P("Yes — for content generation calls", "table_cell")],
    [P("Infrastructure", "table_cell_c"),     P("On-premise GPU server (organisation-owned)", "table_cell"), P("Thin on-premise layer; compute handled by NZ-hosted cloud", "table_cell")],
    [P("Compliance path", "table_cell_c"),    P("Straightforward — no third-party data sharing occurs", "table_cell"), P("Requires a Privacy Impact Assessment and data processing agreement prior to go-live", "table_cell")],
    [P("Voice quality", "table_cell_c"),      P("Very high — approaching commercial studio quality", "table_cell"), P("Commercial studio quality — equivalent to leading market products", "table_cell")],
    [P("Best suited for", "table_cell_c"),    P("Organisations with a strict no-external-cloud policy", "table_cell"), P("Organisations already using managed cloud services and Microsoft 365", "table_cell")],
]

col1 = 3.5*cm
col2 = (W - 4.4*cm - col1) / 2
options_tbl = Table(options_data, colWidths=[col1, col2, col2])
options_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,0), NAVY),
    ("BACKGROUND",    (1,0), (1,0), TEAL),
    ("BACKGROUND",    (2,0), (2,0), colors.HexColor("#1A4B6E")),
    ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, TEAL_LT]),
    ("GRID",          (0,0), (-1,-1), 0.4, SILVER),
    ("TOPPADDING",    (0,0), (-1,-1), 8),
    ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ("RIGHTPADDING",  (0,0), (-1,-1), 8),
    ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ("FONTNAME",      (0,1), (0,-1), "Helvetica-Bold"),
    ("TEXTCOLOR",     (0,1), (0,-1), NAVY),
]))
story.append(options_tbl)

story.append(SP(10))

story.append(callout_box(
    "<b>Note:</b> The architecture is designed so that both deployment options are supported "
    "from a single codebase. An organisation can start with Option B and migrate to Option A "
    "as their infrastructure matures, without rebuilding the product."
))

story.append(SP(16))


# ─── MARKET OPPORTUNITY ───────────────────────────────────────────────────────
story += section_header("Opportunity", "Why This, Why Now")

story.append(P(
    "The global AI voice market is growing rapidly, but the health sector remains significantly "
    "underserved — specifically because existing tools cannot meet its data sovereignty requirements. "
    "This creates a clear window:",
    "body"
))
story.append(SP(8))

opp_points = [
    ("<b>No compliant local alternative exists.</b> Commercial AI voice platforms (including the market leader) operate on external cloud infrastructure incompatible with strict health data requirements.",
    ),
    ("<b>Demand is real and increasing.</b> Health organisations are actively seeking ways to make content more accessible to staff and patients. Audio is a proven format for engagement and retention.",
    ),
    ("<b>The technology is now mature enough.</b> Open, production-grade AI voice technology has reached a quality threshold where the gap between local and commercial cloud solutions is negligible.",
    ),
    ("<b>Microsoft partnership creates a deployment advantage.</b> For organisations already in the Microsoft ecosystem, we can offer a compliant, integrated path to deployment using existing trusted infrastructure.",
    ),
    ("<b>First-mover advantage is significant.</b> Health sector software procurement cycles are long. Being the established compliant solution creates durable competitive positioning.",
    ),
]

for (text,) in opp_points:
    story.append(bullet(text))
    story.append(SP(4))

story.append(SP(10))

story.append(PageBreak())


# ─── WHAT SUCCESS LOOKS LIKE ──────────────────────────────────────────────────
story += section_header("Success Criteria", "What Good Looks Like at Launch")

story.append(P(
    "A successful MVP delivers the following demonstrable outcomes:",
    "body"
))
story.append(SP(8))

success_data = [
    [P("Outcome", "table_hdr"), P("Measure", "table_hdr")],
    [P("Voice persona quality", "table_cell"), P("A listener cannot reliably distinguish the AI voice from the source recording in a blind test", "table_cell")],
    [P("Generation speed", "table_cell"), P("A 5-minute audio piece is generated in under 2 minutes from transcript upload", "table_cell")],
    [P("Data sovereignty", "table_cell"), P("Zero external API calls during content generation — verified with network monitoring", "table_cell")],
    [P("Compliance readiness", "table_cell"), P("Product ships with a completed Data Flow Map and Privacy Impact Assessment template for client use", "table_cell")],
    [P("Usability", "table_cell"), P("A non-technical staff member can create a voice persona and generate their first audio piece within 15 minutes, without training", "table_cell")],
]

success_tbl = Table(success_data, colWidths=[5*cm, W - 4.4*cm - 5.2*cm])
success_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,0), NAVY),
    ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, TEAL_LT]),
    ("GRID",          (0,0), (-1,-1), 0.4, SILVER),
    ("TOPPADDING",    (0,0), (-1,-1), 8),
    ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ("RIGHTPADDING",  (0,0), (-1,-1), 8),
    ("VALIGN",        (0,0), (-1,-1), "TOP"),
]))
story.append(success_tbl)

story.append(SP(16))


# ─── NEXT STEPS ───────────────────────────────────────────────────────────────
story += section_header("Next Steps", "Proposed Path Forward")

steps = [
    ("Alignment", "Team review of this briefing. Agree on the scope of the MVP and which deployment option to prioritise for the initial pitch."),
    ("Proof of Concept", "Internal build of the core voice cloning and audio generation pipeline. Goal: produce a demonstration using a real team member's voice on a sample health transcript."),
    ("Client Identification", "Identify one or two anchor health sector organisations to engage as design partners. Their requirements will shape the compliance documentation and governance workflow."),
    ("Privacy & Legal Review", "Engage legal/privacy counsel to confirm the platform design against NZ HIPC requirements before any client data is processed."),
    ("Pilot Deployment", "Deploy to one design partner organisation in a controlled environment. Gather feedback on voice quality, usability, and workflow fit."),
    ("Commercial Packaging", "Define pricing model, SLA structure, and support offering before broader market engagement."),
]

for i, (title, desc) in enumerate(steps):
    row = Table(
        [[P(str(i+1), "table_hdr"), P(f"<b>{title}</b><br/>{desc}", "body")]],
        colWidths=[1*cm, W - 4.4*cm - 1.2*cm]
    )
    row.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,0), NAVY),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (1,0), (1,0), 12),
        ("LINEBELOW",     (0,0), (-1,0), 0, WHITE),
    ]))
    story.append(KeepTogether([row, SP(5)]))

story.append(SP(12))


# ─── CLOSING ──────────────────────────────────────────────────────────────────
story.append(HR(TEAL, 1))
story.append(SP(10))
story.append(callout_box(
    "This document is intended for internal discussion only. The product concept, "
    "architecture approach, and commercial strategy described herein are proprietary "
    "and confidential. Please do not share outside the team.",
    bg=colors.HexColor("#FEF3C7")
))
story.append(SP(10))
story.append(P("Questions or feedback? Reach out to the project lead directly.", "footer_label"))


# ── Build ──────────────────────────────────────────────────────────────────────
doc.build(story, onFirstPage=on_cover, onLaterPages=on_page)
print(f"PDF written to: {OUTPUT}")
