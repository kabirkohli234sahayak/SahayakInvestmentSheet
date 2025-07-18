import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer,
    Frame, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm
from io import BytesIO
from reportlab.lib.enums import TA_LEFT
from PyPDF2 import PdfMerger
import os

# Static assets
LOGO = "logo.png"
FOOTER = "footer.png"

st.set_page_config(page_title="Investment Sheet Generator", layout="centered")
st.title("Investment Sheet Generator")

# --- Input Fields ---
st.header("Client Information")
client_name = st.text_input("Client Name")
report_date = st.text_input("Date")
financial_goal = st.text_input("Financial Goal")
investment_horizon = st.selectbox("Investment Horizon", ["Short Term", "Medium Term", "Long Term"])
risk_profile = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])

default_return = {"Conservative": "8-10%", "Moderate": "10-12%", "Aggressive": "12-15%"}.get(risk_profile, "")
return_expectation = st.text_input("Return Expectation", value=default_return)
investment_amount = st.text_input("Investment Amount (Lumpsum)")
sip_amount = st.text_input("SIP Amount (Monthly)")

# Strategy Note
include_strategy_note = st.checkbox("Include STP / Hybrid Strategy Description")
strategy_note = ""
if include_strategy_note:
    strategy_note = st.text_area("Strategy Description", height=150, value="""Out of Rs. 35.00 lacs,
• An amount of Rs 7.00 Lacs will be invested directly into Equity Funds.
• Balance amount of Rs. 28.00 lacs will be invested into Debt funds, we will start STP (Systematic Transfer Plan) of Rs. 3.50 lacs every fortnight or according to the market opportunities from Debt Funds to Equity Funds till August 2025.""")

# --- Table Handling ---
def init_df(key, columns):
    if key not in st.session_state:
        st.session_state[key] = pd.DataFrame(columns=columns)

def editable_df(title, key):
    st.subheader(title)
    init_df(key, ["Category", "SubCategory", "Scheme Name", "Allocation (%)", "Amount"])
    return st.data_editor(st.session_state[key], num_rows="dynamic", use_container_width=True, key=key)

def editable_perf_table(key):
    if key not in st.session_state:
        st.session_state[key] = pd.DataFrame([{
            "Scheme Name": "HDFC Mid Cap Fund", "PE": 25.5, "SD": 15.0, "SR": 1.2,
            "Beta": 0.9, "Alpha": 1.5, "1Y": 12.3, "3Y": 15.6, "5Y": 17.8, "10Y": 19.2
        }])
    return st.data_editor(st.session_state[key], num_rows="dynamic", use_container_width=True, key=key)

tables = {}

tables["Lumpsum Allocation"] = st.checkbox("Include Lumpsum Allocation Table")
if tables["Lumpsum Allocation"]:
    tables["Lumpsum Allocation"] = editable_df("Lumpsum Allocation", "lumpsum_df")

tables["SIP Allocation"] = st.checkbox("Include SIP Allocation Table")
if tables["SIP Allocation"]:
    tables["SIP Allocation"] = editable_df("SIP Allocation", "sip_df")

tables["Fund Performance"] = st.checkbox("Include Fund Performance Table")
if tables["Fund Performance"]:
    tables["Fund Performance"] = editable_perf_table("fund_perf_df")

tables["Initial Investment Allocation"] = st.checkbox("Include Initial STP Table")
if tables["Initial Investment Allocation"]:
    tables["Initial Investment Allocation"] = editable_df("Initial Investment Allocation", "initial_stp_df")

tables["Final Portfolio Allocation"] = st.checkbox("Include Final STP Table")
if tables["Final Portfolio Allocation"]:
    tables["Final Portfolio Allocation"] = editable_df("Final Portfolio Allocation", "final_stp_df")

st.markdown("### Fund Factsheet Links")
factsheet_links = st.text_area("Enter links in format:\nFund Name - Description | https://link.com", height=150)

# --- PDF Utilities ---
def dataframe_to_table(df):
    df = df.dropna(how='all')
    data = [list(df.columns)] + df.astype(str).values.tolist()
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), HexColor('#E6F3F8')),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    return table

def fund_perf_table(df):
    df = df.dropna(how='all')
    cols = ['Scheme Name', 'PE', 'SD', 'SR', 'Beta', 'Alpha', '1Y', '3Y', '5Y', '10Y']
    df = df[cols]
    data = [
        ['', 'Ratios', '', '', '', '', 'Returns', '', '', ''],
        cols
    ] + df.astype(str).values.tolist()
    col_widths = [5.0*cm] + [1.2*cm]*9
    table = Table(data, colWidths=col_widths, repeatRows=2)
    table.setStyle(TableStyle([
        ('SPAN', (1, 0), (5, 0)),
        ('SPAN', (6, 0), (9, 0)),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BACKGROUND', (0,0), (-1,1), HexColor('#E6F3F8')),
    ]))
    return table

def add_header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    if os.path.exists(LOGO):
        canvas.drawImage(LOGO, 260, 130, width=80, preserveAspectRatio=True, mask='auto')
    if os.path.exists(FOOTER):
        canvas.drawImage(FOOTER, 0, 0, width=width, preserveAspectRatio=True, mask='auto')
    canvas.setFont('Helvetica', 8)
    canvas.drawCentredString(width / 2.0, 15, str(doc.page))
    if doc.page < doc.pageCount:  # Hide on disclaimer page
        canvas.drawRightString(width - 30, 15, "Note: Please check the Disclaimer on the last page")
    canvas.restoreState()

# --- PDF Generation ---
def generate_pdf():
    buffer = BytesIO()
    styles = getSampleStyleSheet()
    heading = ParagraphStyle(name='HeadingLarge', fontSize=20, alignment=1, spaceAfter=20)
    normal = ParagraphStyle(name='Normal', spaceAfter=6, leading=14)

    elements = [Paragraph("Investment Sheet", heading)]
    elements += [Paragraph(f"<b>{label}:</b> {value}", normal) for label, value in [
        ("Client Name", client_name),
        ("Date", report_date),
        ("Financial Goal", financial_goal),
        ("Investment Horizon", investment_horizon),
        ("Risk Profile", risk_profile),
        ("Return Expectation", return_expectation),
        ("Investment Amount", f"Rs. {investment_amount} (Lumpsum), Rs. {sip_amount} (SIP)")
    ]]

    if include_strategy_note and strategy_note:
        elements += [Spacer(1, 10), Paragraph("<b>Investment Strategy</b>", styles['Heading4'])]
        for line in strategy_note.strip().splitlines():
            elements.append(Paragraph(line.strip(), normal))

    for title, df in tables.items():
        if isinstance(df, pd.DataFrame) and not df.empty:
            elements.append(Spacer(1, 10))
            elements.append(KeepTogether([
                Paragraph(f"<b>{title}</b>", styles['Heading4']),
                fund_perf_table(df) if title == "Fund Performance" else dataframe_to_table(df)
            ]))

    if factsheet_links.strip():
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("<b>Fund Factsheet Links</b>", styles['Heading4']))
        for line in factsheet_links.strip().splitlines():
            if "|" in line:
                text, url = line.split("|")
                elements.append(Paragraph(f"{text.strip()}: <a href='{url.strip()}'>{url.strip()}</a>", normal))
            else:
                elements.append(Paragraph(line.strip(), normal))

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<b>Disclaimer</b>", styles['Heading3']))
    disclaimer = """Any information provided by Sahayak & their associates does not constitute an investment advice..."""
    for line in disclaimer.strip().splitlines():
        elements.append(Paragraph(line.strip(), normal))

    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=80, bottomMargin=60)
    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    buffer.seek(0)
    return buffer

# --- Trigger Button ---
if st.button("Generate PDF"):
    if not client_name or not report_date:
        st.warning("Please fill in Client Name and Date before generating the PDF.")
    else:
        pdf = generate_pdf()
        st.success("✅ PDF generated successfully!")
        st.download_button("📥 Download PDF", data=pdf, file_name="Investment_Sheet.pdf", mime="application/pdf")
