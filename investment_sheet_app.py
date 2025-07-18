import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Frame, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm
from io import BytesIO, StringIO
import os
from PyPDF2 import PdfMerger
from reportlab.lib.enums import TA_LEFT

# File paths for images. Assumes they are in the same directory as the script.
LOGO = "logo.png"
FOOTER = "footer.png"

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

# --- Table Input using Text Areas ---
def display_csv_input(title, default_csv):
    st.subheader(title)
    st.markdown("Paste your data below in CSV format (comma-separated). The first row should be the column headers.")
    return st.text_area(title, value=default_csv, height=200)

csv_defaults = {
    'lumpsum': "Category,SubCategory,Scheme Name,Allocation (%),Amount\n",
    'sip': "Category,SubCategory,Scheme Name,Allocation (%),Amount\n",
    'fund_perf': "Scheme Name,PE,SD,SR,Beta,Alpha,1Y,3Y,5Y,10Y\nHDFC Mid Cap Fund,25.5,15.0,1.2,0.9,1.5,12.3,15.6,17.8,19.2",
    'initial_stp': "Category,SubCategory,Scheme Name,Allocation (%),Amount\n",
    'final_stp': "Category,SubCategory,Scheme Name,Allocation (%),Amount\n"
}

include_lumpsum = st.checkbox("Include Lumpsum Allocation Table")
lumpsum_csv = ""
if include_lumpsum:
    lumpsum_csv = display_csv_input("Lumpsum Allocation", csv_defaults['lumpsum'])

include_sip = st.checkbox("Include SIP Allocation Table")
sip_csv = ""
if include_sip:
    sip_csv = display_csv_input("SIP Allocation", csv_defaults['sip'])

include_fund_perf = st.checkbox("Include Fund Performance Table")
fund_perf_csv = ""
if include_fund_perf:
    fund_perf_csv = display_csv_input("Fund Performance", csv_defaults['fund_perf'])

include_initial_stp = st.checkbox("Include Initial Investment Table (STP Clients Only)")
initial_stp_csv = ""
if include_initial_stp:
    initial_stp_csv = display_csv_input("Initial Investment Allocation", csv_defaults['initial_stp'])

include_final_stp = st.checkbox("Include Final Portfolio Table (Post STP)")
final_stp_csv = ""
if include_final_stp:
    final_stp_csv = display_csv_input("Final Portfolio Allocation", csv_defaults['final_stp'])

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
    
    display_columns = ['Scheme Name', 'PE', 'SD', 'SR', 'Beta', 'Alpha', '1Y', '3Y', '5Y', '10Y']
    
    missing_cols = [col for col in display_columns if col not in df.columns]
    if missing_cols:
        st.warning(f"The following columns were not found in your input and will be skipped in the Fund Performance table: {', '.join(missing_cols)}")
        
    df_display = df.reindex(columns=display_columns)

    header_row1 = ['', 'Ratios', '', '', '', '', 'Returns', '', '', '']
    header_row2 = list(df_display.columns)
    
    data = [header_row1, header_row2] + df_display.astype(str).values.tolist()
    
    col_widths = [5.0 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm]
    
    table = Table(data, colWidths=col_widths, repeatRows=2)
    
    table.setStyle(TableStyle([
        ('SPAN', (1, 0), (5, 0)),
        ('SPAN', (6, 0), (-1, 0)),
        ('ALIGN', (1, 0), (5, 0), 'CENTER'),
        ('ALIGN', (6, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,2), (-1,-1), 'RIGHT'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BACKGROUND', (0,0), (-1,1), HexColor('#E6F3F8')),
        ('LINEBELOW', (0,0), (-1,1), 1, colors.black),
        ('LINEABOVE', (0,0), (-1,0), 1, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 1, colors.black),
    ]))
    return table

def main_header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    if os.path.exists(LOGO):
        canvas.drawImage(LOGO, 260, 130, width=80, preserveAspectRatio=True, mask='auto')
    if os.path.exists(FOOTER):
        canvas.drawImage(FOOTER, 0, 0, width=width, preserveAspectRatio=True, mask='auto')
    
    page_number_text = "%d" % doc.page
    canvas.setFont('Helvetica', 9)
    canvas.drawCentredString(width/2.0, 15, page_number_text)

    note_text = "Note: Please check the Disclaimer on the last page"
    note_style = ParagraphStyle(
        name='NoteStyle',
        fontSize=7,
        leading=10,
        alignment=TA_LEFT
    )
    note_paragraph = Paragraph(note_text, note_style)
    
    frame_x = width - 150
    frame_y = 15
    frame_width = 135
    frame_height = 20

    note_frame = Frame(
        frame_x,
        frame_y,
        frame_width,
        frame_height,
        leftPadding=0,
        bottomPadding=0,
        rightPadding=0,
        topPadding=0,
        id='note_frame'
    )
    note_frame.addFromList([note_paragraph], canvas)

    canvas.restoreState()

def disclaimer_header_footer(canvas, doc, start_page_num):
    canvas.saveState()
    width, height = A4
    if os.path.exists(LOGO):
        canvas.drawImage(LOGO, 260, 130, width=80, preserveAspectRatio=True, mask='auto')
    if os.path.exists(FOOTER):
        canvas.drawImage(FOOTER, 0, 0, width=width, preserveAspectRatio=True, mask='auto')
    
    page_number_text = "%d" % (start_page_num + doc.page)
    canvas.setFont('Helvetica', 9)
    canvas.drawCentredString(width/2.0, 15, page_number_text)
    
    canvas.restoreState()

def generate_disclaimer_pdf(start_page_num):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    disclaimer_style = ParagraphStyle(name='DisclaimerStyle', parent=styles['Normal'])
    
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
    
    doc.build(disclaimer_elements, onFirstPage=lambda c, d: disclaimer_header_footer(c, d, start_page_num), onLaterPages=lambda c, d: disclaimer_header_footer(c, d, start_page_num))
    
    buffer.seek(0)
    return buffer

# --- PDF Generator ---
def generate_pdf():
    tables_to_process = {
        'lumpsum': lumpsum_csv,
        'sip': sip_csv,
        'fund_perf': fund_perf_csv,
        'initial_stp': initial_stp_csv,
        'final_stp': final_stp_csv
    }

    processed_tables = {}
    for key, csv_data in tables_to_process.items():
        if csv_data.strip():
            try:
                df = pd.read_csv(StringIO(csv_data))
                processed_tables[key] = df
            except pd.errors.EmptyDataError:
                continue
            except Exception as e:
                st.error(f"Error parsing {key} data: {e}")
                return None

    try:
        lumpsum_total = float(investment_amount.replace(",", "")) if investment_amount else 0
        sip_total = float(sip_amount.replace(",", "")) if sip_amount else 0
    except (ValueError, AttributeError):
        lumpsum_total = 0
        sip_total = 0

    if 'lumpsum' in processed_tables and lumpsum_total > 0:
        df = processed_tables['lumpsum']
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        df['Allocation (%)'] = (df['Amount'] / lumpsum_total) * 100
        processed_tables['lumpsum'] = df

    if 'sip' in processed_tables and sip_total > 0:
        df = processed_tables['sip']
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        df['Allocation (%)'] = (df['Amount'] / sip_total) * 100
        processed_tables['sip'] = df

    if 'initial_stp' in processed_tables and lumpsum_total > 0:
        df = processed_tables['initial_stp']
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        df['Allocation (%)'] = (df['Amount'] / lumpsum_total) * 100
        processed_tables['initial_stp'] = df

    if 'final_stp' in processed_tables and lumpsum_total > 0:
        df = processed_tables['final_stp']
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        df['Allocation (%)'] = (df['Amount'] / lumpsum_total) * 100
        processed_tables['final_stp'] = df

    main_buffer = BytesIO()
    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle(name='HeadingLarge', fontSize=20, leading=24, alignment=1, spaceAfter=20)
    client_style = ParagraphStyle(name='ClientDetails', parent=styles['Normal'], spaceAfter=6, leading=14)
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
    ]

    if include_strategy_note and strategy_note:
        elements += [
            Spacer(1, 0.5*cm),
            Paragraph("<b>Investment Strategy</b>", styles['Heading4']),
            Paragraph(strategy_note, styles['Normal'])
        ]

    if 'lumpsum' in processed_tables:
        elements += [Spacer(1, 0.5*cm), KeepTogether([Paragraph("<b>Lumpsum Allocation</b>", styles['Heading4']), dataframe_to_table(processed_tables['lumpsum'])])]
    if 'sip' in processed_tables:
        elements += [Spacer(1, 0.5*cm), KeepTogether([Paragraph("<b>SIP Allocation</b>", styles['Heading4']), dataframe_to_table(processed_tables['sip'])])]
    if 'fund_perf' in processed_tables:
        elements += [Spacer(1, 0.5*cm), KeepTogether([Paragraph("<b>Fund Performance</b>", styles['Heading4']), fund_performance_table(processed_tables['fund_perf'])])]
    if 'initial_stp' in processed_tables:
        elements += [Spacer(1, 0.5*cm), KeepTogether([Paragraph("<b>Initial Investment Allocation</b>", styles['Heading4']), dataframe_to_table(processed_tables['initial_stp'])])]
    if 'final_stp' in processed_tables:
        elements += [Spacer(1, 0.5*cm), KeepTogether([Paragraph("<b>Final Portfolio Allocation</b>", styles['Heading4']), dataframe_to_table(processed_tables['final_stp'])])]

    if factsheet_links:
        elements += [
            Spacer(1, 0.5*cm),
            Paragraph("<b>Fund Factsheet Links</b>", styles['Heading4']),
        ]
        for link in factsheet_links.strip().split('\n'):
            if link:
                parts = link.split('|')
                if len(parts) == 2:
                    text = parts[0].strip()
                    url = parts[1].strip()
                    elements.append(Paragraph(f'<link href="{url}">{url}</link>', styles['Normal']))

    main_doc = SimpleDocTemplate(main_buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=80, bottomMargin=60)
    main_doc.build(elements, onFirstPage=main_header_footer, onLaterPages=main_header_footer)
    main_buffer.seek(0)
    
    disclaimer_buffer = generate_disclaimer_pdf(len(main_doc.pages))
    
    merger = PdfMerger()
    merger.append(main_buffer)
    merger.append(disclaimer_buffer)
    
    merged_pdf_buffer = BytesIO()
    merger.write(merged_pdf_buffer)
    merger.close()
    merged_pdf_buffer.seek(0)
    
    return merged_pdf_buffer

# --- Download Button ---
if st.button("Generate PDF"):
    if not client_name or not report_date:
        st.warning("Please fill in Client Name and Date before generating the PDF.")
    else:
        with st.spinner("Generating PDF..."):
            pdf_buffer = generate_pdf()
            if pdf_buffer:
                st.download_button(
                    label="Download PDF",
                    data=pdf_buffer,
                    file_name=f"Investment_Sheet - {client_name}.pdf",
                    mime="application/pdf"
                )
