import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, FrameBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm
from io import BytesIO
import os
from PyPDF2 import PdfMerger
from reportlab.platypus import KeepTogether
from reportlab.lib.enums import TA_LEFT

# Static assets
LOGO = "static/logo.png"
FOOTER = "static/footer.png"

st.set_page_config(page_title="Investment Sheet Generator", layout="centered")
st.title("Investment Sheet Generator")

# --- Client Info ---
st.header("Client Information")
client_name = st.text_input("Client Name")
report_date = st.text_input("Date")
financial_goal = st.text_input("Financial Goal")
investment_horizon = st.selectbox("Investment Horizon", ["Short Term", "Medium Term", "Long Term"])
risk_profile = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])

# Autofill return expectation based on risk profile
default_return_expectation = ""
if risk_profile == "Aggressive":
    default_return_expectation = "12-15%"
elif risk_profile == "Moderate":
    default_return_expectation = "10-12%"
elif risk_profile == "Conservative":
    default_return_expectation = "8-10%"
    
return_expectation = st.text_input("Return Expectation", value=default_return_expectation)

investment_amount = st.text_input("Investment Amount (Lumpsum)")
sip_amount = st.text_input("SIP Amount (Monthly)")

# --- Optional Strategy Note ---
include_strategy_note = st.checkbox("Include STP / Hybrid Strategy Description")
if include_strategy_note:
    st.markdown("### Investment Strategy Note")
    strategy_note = st.text_area("STP or Hybrid Investment Strategy Description", value="""Out of Rs. 35.00 lacs,
• An amount of Rs 7.00 Lacs will be invested directly into Equity Funds.
• Balance amount of Rs. 28.00 lacs will be invested into Debt funds, we will start STP (Systematic Transfer Plan) of Rs. 3.50 lacs every fortnight or according to the market opportunities from Debt Funds to Equity Funds till August 2025.""", height=150)

# --- Tables ---
def editable_table(title, default_rows, key):
    st.subheader(title)
    df = pd.DataFrame(default_rows if default_rows else [{"Category": "", "SubCategory": "", "Scheme Name": "", "Allocation (%)": "", "Amount": ""}])
    return st.data_editor(df, num_rows="dynamic", use_container_width=True, key=key)

include_lumpsum = st.checkbox("Include Lumpsum Allocation Table")
if include_lumpsum:
    lumpsum_alloc = editable_table("Lumpsum Allocation", [{"Category": "Equity", "SubCategory": "Mid Cap", "Scheme Name": "HDFC Mid Cap Fund", "Allocation (%)": 50, "Amount": 100000}], key="lumpsum")

include_sip = st.checkbox("Include SIP Allocation Table")
if include_sip:
    sip_alloc = editable_table("SIP Allocation", [{"Category": "Equity", "SubCategory": "Small Cap", "Scheme Name": "SBI Small Cap Fund", "Allocation (%)": 50, "Amount": 5000}], key="sip")

include_fund_perf = st.checkbox("Include Fund Performance Table")
if include_fund_perf:
    st.subheader("Fund Performance")
    fund_perf_data = [{"Scheme Name": "HDFC Mid Cap Fund", "PE": 25.5, "SD": 15.0, "SR": 1.2, "Beta": 0.9, "Alpha": 1.5, "1Y": 12.3, "3Y": 15.6, "5Y": 17.8, "10Y": 19.2}]
    fund_perf = st.data_editor(pd.DataFrame(fund_perf_data), num_rows="dynamic", use_container_width=True, key="fund_perf")

include_initial_stp = st.checkbox("Include Initial Investment Table (STP Clients Only)")
if include_initial_stp:
    initial_alloc = editable_table("Initial Investment Allocation", [], key="initial_stp")

include_final_stp = st.checkbox("Include Final Portfolio Table (Post STP)")
if include_final_stp:
    final_alloc = editable_table("Final Portfolio Allocation", [], key="final_stp")

st.markdown("### Fund Factsheet Links")
factsheet_links = st.text_area("Enter links in the format:\n1. Fund Name - Description | https://link.com", height=150)

# --- PDF Helpers ---
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

def fund_performance_table(df):
    df = df.dropna(how='all')
    
    # Filter and reorder columns
    display_columns = ['Scheme Name', 'PE', 'SD', 'SR', 'Beta', 'Alpha', '1Y', '3Y', '5Y', '10Y']
    
    # Ensure all required columns exist before selecting
    missing_cols = [col for col in display_columns if col not in df.columns]
    if missing_cols:
        st.warning(f"The following columns were not found in your input and will be skipped in the Fund Performance table: {', '.join(missing_cols)}")
        
    df_display = df.reindex(columns=display_columns)

    # Create a two-row header
    header_row1 = ['', 'Ratios', '', '', '', '', 'Returns', '', '', '']
    header_row2 = list(df_display.columns)
    
    data = [header_row1, header_row2] + df_display.astype(str).values.tolist()
    
    # Set column widths to accommodate the new column order and number
    col_widths = [5.0 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm]
    
    table = Table(data, colWidths=col_widths, repeatRows=2)
    
    table.setStyle(TableStyle([
        ('SPAN', (1, 0), (5, 0)),
        ('SPAN', (6, 0), (-1, 0)),
        ('ALIGN', (1, 0), (5, 0), 'CENTER'),
        ('ALIGN', (6, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,2), (-1,-1), 'RIGHT'), # Align all numerical data to the right (starting from the third row)
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BACKGROUND', (0,0), (-1,1), HexColor('#E6F3F8')),
        ('LINEBELOW', (0,0), (-1,1), 1, colors.black), # Thicker line below the header
        ('LINEABOVE', (0,0), (-1,0), 1, colors.black), # Thicker line above header
        ('LINEBELOW', (0,-1), (-1,-1), 1, colors.black), # Thicker line at the bottom
    ]))
    return table

def header_footer_with_logos(canvas, doc):
    canvas.saveState()
    width, height = A4
    if os.path.exists(LOGO):
        canvas.drawImage(LOGO, 260, 130, width=80, preserveAspectRatio=True, mask='auto')
    if os.path.exists(FOOTER):
        canvas.drawImage(FOOTER, 0, 0, width=width, preserveAspectRatio=True, mask='auto')
    
    page_number_text = "%d" % doc.page
    canvas.setFont('Helvetica', 9)
    canvas.drawCentredString(width/2.0, 15, page_number_text)
    
    canvas.restoreState()

# --- PDF Generator ---
def generate_pdf():
    buffer = BytesIO()
    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle(name='HeadingLarge', fontSize=20, leading=24, alignment=1, spaceAfter=20)
    client_style = ParagraphStyle(name='ClientDetails', parent=styles['Normal'], spaceAfter=6, leading=14)
    disclaimer_style = ParagraphStyle(name='DisclaimerStyle', parent=styles['Normal'])
    note_style = ParagraphStyle(name='NoteStyle', fontSize=7, leading=10)

    elements = [Paragraph("Investment Sheet", heading_style)]
    elements += [
        Paragraph(f"<b>Client Name:</b> {client_name}", client_style),
        Paragraph(f"<b>Date:</b> {report_date}", client_style),
        Paragraph(f"<b>Financial Goal:</b> {financial_goal}", client_style),
        Paragraph(f"<b>Investment Horizon:</b> {investment_horizon}", client_style),
        Paragraph(f"<b>Risk Profile:</b> {risk_profile}", client_style),
        Paragraph(f"<b>Return Expectation:</b> {return_expectation}", client_style),
        Paragraph(f"<b>Investment Amount:</b> Rs. {investment_amount} (Lumpsum), Rs. {sip_amount} (SIP)", client_style),
        Spacer(1, 10),
    ]
    
    bullet_style = ParagraphStyle(name='BulletStyle', parent=styles['Normal'], leftIndent=20, firstLineIndent=-15, spaceBefore=0)

    if include_strategy_note:
        elements.append(Paragraph("<b>Investment Strategy</b>", styles['Heading3']))
        strategy_lines = strategy_note.strip().split("• ")
        for line in strategy_lines:
            if line:
                elements.append(Paragraph(f"• {line.strip()}", bullet_style))
        elements.append(Spacer(1, 10))

    tables = []
    if include_lumpsum:
        tables.append(("Lumpsum Allocation", lumpsum_alloc))
    if include_sip:
        tables.append(("SIP Allocation", sip_alloc))
    if include_fund_perf:
        tables.append(("Fund Performance", fund_perf))
    if include_initial_stp:
        tables.append(("Initial Investment Allocation", initial_alloc))
    if include_final_stp:
        tables.append(("Final Portfolio Allocation", final_alloc))
        
    for title, df in tables:
        if not df.empty:
            table_heading = Paragraph(f"<b>{title}</b>", styles['Heading4'])
            
            if title == "Fund Performance":
                table_content = fund_performance_table(df)
            else:
                table_content = dataframe_to_table(df)
            
            table_elements = [
                table_heading,
                Spacer(1, 10),
                table_content
            ]

            note_text = ""
            if title == "Initial Investment Allocation":
                note_text = "*First time transaction to be done for switching purpose from Debt funds to Equity Funds"
            elif title == "Final Portfolio Allocation":
                note_text = "*Final Portfolio Illustration after switching the funds from Debt to Equity."

            if note_text:
                note_paragraph_style = ParagraphStyle('note_paragraph_style', parent=note_style, leftIndent=0, firstLineIndent=0, spaceBefore=0, leading=10, fontSize=7)
                note_paragraph = Paragraph(note_text, note_paragraph_style)
                note_table = Table([[note_paragraph]], colWidths=[table_content._argW[0]])
                note_table.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0)]))
                table_elements.append(note_table)
            
            elements.append(KeepTogether(table_elements))
            elements.append(Spacer(1, 10))

    if factsheet_links.strip():
        elements.append(Paragraph("<b>Fund Factsheets</b>", styles['Heading4']))
        for line in factsheet_links.strip().splitlines():
            if "|" in line:
                label, url = line.split("|")
                elements.append(Paragraph(f"{label.strip()}: <a href='{url.strip()}'>{url.strip()}</a>", styles['Normal']))
            else:
                elements.append(Paragraph(line.strip(), styles['Normal']))

    # Force a new page for the final disclaimer
    elements.append(FrameBreak())
    
    disclaimer_text = """Any information provided by Sahayak & their associates does not constitute an investment advice, offer, invitation & inducement to invest in securities or other investments and Sahayak is not soliciting any action based on it. 
Keep in mind that investing involves risk. The value of your investment will fluctuate over time, and you may gain or lose money / original capital. 
Guidance provided by Sahayak is purely educational. Sahayak doesn’t guarantee that the information disseminated herein would result in any monetary or financial gains or loss as the information is purely educational & based on past returns & performance. 
Past performance is not a guide for future performance. Future returns are not guaranteed, and loss of original capital may occur. 
Before acting on any information, investor should consider whether it is suitable for their particular circumstances and if necessary, seek professional investment advice from a Registered Investment Advisor. 
All investments especially mutual fund investments are subject to market risks. Kindly read the Offer Documents carefully before investing. 
Sahayak does not provide legal or tax advice. The information herein is general and educational in nature and should not be considered legal or tax advice.
Tax laws and regulations are complex and subject to change, which can materially impact investment results. 
Sahayak doesn't guarantee that the information provided herein is accurate, complete, or timely. 
Sahayak makes no warranties with regard to such information or results obtained by its use, and disclaim any liability arising out of your use of, or any tax position taken in reliance on such information. 
Sahayak is a distributor of financial products and NOT an investment advisor and NOT Authorized to provide any investment advice by SEBI. 
Sahayak Associates is an AMFI Registered Mutual Fund Distributor only.
"""
    disclaimer_elements = [Paragraph("<b>Disclaimer</b>", styles['Heading3'])] + [
        Paragraph(line.strip(), disclaimer_style) for line in disclaimer_text.strip().splitlines()
    ]
    elements.extend(disclaimer_elements)

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    doc.build(elements, onFirstPage=header_footer_with_logos, onLaterPages=header_footer_with_logos)
    
    buffer.seek(0)
    return buffer

if st.button("Generate PDF"):
    pdf = generate_pdf()
    st.success("PDF generated successfully!")
    st.download_button("Download PDF", data=pdf, file_name="Investment_Sheet.pdf", mime="application/pdf")