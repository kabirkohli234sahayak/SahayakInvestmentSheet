import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    Table, TableStyle, SimpleDocTemplate, Paragraph,
    Spacer, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import cm
from io import BytesIO
import os
from PyPDF2 import PdfMerger

LOGO = "logo.png"
FOOTER = "footer.png"

st.set_page_config(page_title="Investment Sheet Generator", layout="centered")
st.title("Investment Sheet Generator")

# --- Input Fields ---
client_name = st.text_input("Client Name")
report_date = st.text_input("Date")
financial_goal = st.text_input("Financial Goal")
investment_horizon = st.selectbox("Investment Horizon", ["Short Term", "Medium Term", "Long Term"])
risk_profile = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])

default_return = {"Aggressive": "12-15%", "Moderate": "10-12%", "Conservative": "8-10%"}
return_expectation = st.text_input("Return Expectation", default_return.get(risk_profile, ""))

investment_amount = st.text_input("Investment Amount (Lumpsum)")
sip_amount = st.text_input("SIP Amount (Monthly)")

# Strategy Note
include_strategy = st.checkbox("Include STP / Hybrid Strategy Description")
if include_strategy:
    st.markdown("### Investment Strategy Note")
    strategy_note = st.text_area("Enter bullet points using '-' or '*'", value="""- Rs. 7 Lacs in Equity Funds\n- Rs. 28 Lacs in Debt Funds via STP till Aug 2025""")

# Table Data
def editable_df(title, key):
    st.subheader(title)
    if key not in st.session_state:
        st.session_state[key] = pd.DataFrame(columns=["Category", "SubCategory", "Scheme Name", "Allocation (%)", "Amount"])
    st.session_state[key] = st.data_editor(st.session_state[key], num_rows="dynamic", use_container_width=True, key=key)
    return st.session_state[key]

include_tables = {}

include_tables["Lumpsum Allocation"] = st.checkbox("Include Lumpsum Allocation Table")
if include_tables["Lumpsum Allocation"]:
    lumpsum_df = editable_df("Lumpsum Allocation", "lumpsum_df")

include_tables["SIP Allocation"] = st.checkbox("Include SIP Allocation Table")
if include_tables["SIP Allocation"]:
    sip_df = editable_df("SIP Allocation", "sip_df")

include_tables["Fund Performance"] = st.checkbox("Include Fund Performance Table")
if include_tables["Fund Performance"]:
    fund_df = editable_df("Fund Performance", "fund_perf_df")

include_tables["Initial Investment Allocation"] = st.checkbox("Include Initial STP Table")
if include_tables["Initial Investment Allocation"]:
    initial_df = editable_df("Initial STP Allocation", "initial_stp_df")

include_tables["Final Portfolio Allocation"] = st.checkbox("Include Final STP Table")
if include_tables["Final Portfolio Allocation"]:
    final_df = editable_df("Final Portfolio Allocation", "final_stp_df")

# Factsheets
st.markdown("### Fund Factsheet Links")
factsheet_links = st.text_area("Enter links (1. Label | https://url)", height=150)

# PDF Helpers
def dataframe_to_table(df):
    df = df.dropna(how='all')
    data = [list(df.columns)] + df.astype(str).values.tolist()
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    return table

def main_header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    if os.path.exists(LOGO):
        canvas.drawImage(LOGO, 260, 130, width=80, preserveAspectRatio=True)
    if os.path.exists(FOOTER):
        canvas.drawImage(FOOTER, 0, 0, width=width, preserveAspectRatio=True)
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(width / 2.0, 15, f"Page {doc.page}")
    if doc.page != doc.page_count:  # Avoid on last page
        canvas.drawRightString(width - 30, 15, "Note: Please check the Disclaimer on the last page")
    canvas.restoreState()

def disclaimer_page(canvas, doc):
    canvas.saveState()
    width, height = A4
    if os.path.exists(FOOTER):
        canvas.drawImage(FOOTER, 0, 0, width=width, preserveAspectRatio=True)
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(width / 2.0, 15, f"Page {doc.page}")
    canvas.restoreState()

def build_pdf():
    buf = BytesIO()
    styles = getSampleStyleSheet()
    heading_style = styles['Heading1']
    normal_style = styles['Normal']
    note_style = ParagraphStyle(name='Note', fontSize=7, textColor=colors.black)

    elements = [Paragraph("Investment Sheet", heading_style)]
    elements += [
        Paragraph(f"<b>Client Name:</b> {client_name}", normal_style),
        Paragraph(f"<b>Date:</b> {report_date}", normal_style),
        Paragraph(f"<b>Financial Goal:</b> {financial_goal}", normal_style),
        Paragraph(f"<b>Investment Horizon:</b> {investment_horizon}", normal_style),
        Paragraph(f"<b>Risk Profile:</b> {risk_profile}", normal_style),
        Paragraph(f"<b>Return Expectation:</b> {return_expectation}", normal_style),
        Paragraph(f"<b>Investment Amount:</b> Rs. {investment_amount}, SIP: Rs. {sip_amount}", normal_style),
        Spacer(1, 12)
    ]

    if include_strategy:
        elements.append(Paragraph("<b>Investment Strategy</b>", styles['Heading3']))
        for line in strategy_note.splitlines():
            if line.strip().startswith(("-", "*")):
                elements.append(Paragraph(f"• {line.strip()[1:].strip()}", normal_style))
            else:
                elements.append(Paragraph(line.strip(), normal_style))
        elements.append(Spacer(1, 12))

    for title in include_tables:
        if include_tables[title] and not st.session_state[title.lower().replace(" ", "_") + "_df"].empty:
            df = st.session_state[title.lower().replace(" ", "_") + "_df"]
            block = [
                Paragraph(f"<b>{title}</b>", styles['Heading4']),
                dataframe_to_table(df)
            ]
            if title == "Initial Investment Allocation":
                block.append(Paragraph("*Initial investment before switching to equity", note_style))
            if title == "Final Portfolio Allocation":
                block.append(Paragraph("*Final structure after STP is complete", note_style))
            elements.append(KeepTogether(block))
            elements.append(Spacer(1, 12))

    if factsheet_links.strip():
        elements.append(Paragraph("<b>Fund Factsheets</b>", styles['Heading4']))
        for line in factsheet_links.strip().splitlines():
            if "|" in line:
                text, url = line.split("|")
                elements.append(Paragraph(f"{text.strip()}: <a href='{url.strip()}'>{url.strip()}</a>", normal_style))
            else:
                elements.append(Paragraph(line.strip(), normal_style))

    # Disclaimer
    elements.append(PageBreak())
    disclaimer_text = """
Any information provided by Sahayak & their associates does not constitute investment advice...
Sahayak is a distributor of financial products and NOT an investment advisor and NOT authorized to provide any investment advice by SEBI.
"""
    elements.append(Paragraph("<b>Disclaimer</b>", styles['Heading3']))
    for line in disclaimer_text.strip().splitlines():
        elements.append(Paragraph(line.strip(), normal_style))

    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=100, bottomMargin=60)
    doc.build(elements, onFirstPage=main_header_footer, onLaterPages=main_header_footer)
    buf.seek(0)
    return buf

# --- Streamlit Trigger ---
if st.button("Generate PDF"):
    if not client_name or not report_date:
        st.warning("Please fill in required fields!")
    else:
        pdf = build_pdf()
        st.success("PDF generated successfully!")
        st.download_button("Download PDF", data=pdf, file_name=f"{client_name}_Investment_Sheet.pdf", mime="application/pdf")
