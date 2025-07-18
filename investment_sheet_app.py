import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Frame, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm
from io import BytesIO
import os
from PyPDF2 import PdfMerger
from reportlab.lib.enums import TA_LEFT

# File paths for images. Assumes they are in the same directory as the script.
# You will need to make sure these files exist in the same directory.
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

# --- Table State Management & Generation ---
if 'lumpsum_df' not in st.session_state:
    st.session_state.lumpsum_df = pd.DataFrame(columns=["Category", "SubCategory", "Scheme Name", "Allocation (%)", "Amount"])
if 'sip_df' not in st.session_state:
    st.session_state.sip_df = pd.DataFrame(columns=["Category", "SubCategory", "Scheme Name", "Allocation (%)", "Amount"])
    
if 'fund_perf_df' not in st.session_state:
    st.session_state.fund_perf_df = pd.DataFrame([{"Scheme Name": "HDFC Mid Cap Fund", "PE": 25.5, "SD": 15.0, "SR": 1.2, "Beta": 0.9, "Alpha": 1.5, "1Y": 12.3, "3Y": 15.6, "5Y": 17.8, "10Y": 19.2}])
if 'initial_stp_df' not in st.session_state:
    st.session_state.initial_stp_df = pd.DataFrame(columns=["Category", "SubCategory", "Scheme Name", "Allocation (%)", "Amount"])
if 'final_stp_df' not in st.session_state:
    st.session_state.final_stp_df = pd.DataFrame(columns=["Category", "SubCategory", "Scheme Name", "Allocation (%)", "Amount"])

def display_editable_table(title, df_key):
    st.subheader(title)
    # The data_editor now handles all state updates implicitly
    st.data_editor(st.session_state[df_key], num_rows="dynamic", use_container_width=True, key=df_key)


include_lumpsum = st.checkbox("Include Lumpsum Allocation Table")
if include_lumpsum:
    display_editable_table("Lumpsum Allocation", 'lumpsum_df')

include_sip = st.checkbox("Include SIP Allocation Table")
if include_sip:
    display_editable_table("SIP Allocation", 'sip_df')

include_fund_perf = st.checkbox("Include Fund Performance Table")
if include_fund_perf:
    display_editable_table("Fund Performance", 'fund_perf_df')

include_initial_stp = st.checkbox("Include Initial Investment Table (STP Clients Only)")
if include_initial_stp:
    display_editable_table("Initial Investment Allocation", 'initial_stp_df')

include_final_stp = st.checkbox("Include Final Portfolio Table (Post STP)")
if include_final_stp:
    display_editable_table("Final Portfolio Allocation", 'final_stp_df')


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
    
    # Page number
    page_number_text = "%d" % doc.page
    canvas.setFont('Helvetica', 9)
    canvas.drawCentredString(width/2.0, 15, page_number_text)

    # Note at the bottom right using Paragraph and Frame for proper wrapping
    note_text = "Note: Please check the Disclaimer on the last page"
    
    # Define a style for the note
    note_style = ParagraphStyle(
        name='NoteStyle',
        fontSize=7,
        leading=10,
        alignment=TA_LEFT
    )
    
    # Create the paragraph object
    note_paragraph = Paragraph(note_text, note_style)
    
    # Calculate the position and size of the frame for the note
    frame_x = width - 150 # Start 150 points from the right edge
    frame_y = 15          # Start 15 points from the bottom edge
    frame_width = 135
    frame_height = 20

    # Create the frame
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

    # Render the paragraph inside the frame
    note_frame.addFromList([note_paragraph], canvas)

    canvas.restoreState()

def disclaimer_header_footer(canvas, doc, start_page_num):
    canvas.saveState()
    width, height = A4
    if os.path.exists(LOGO):
        canvas.drawImage(LOGO, 260, 130, width=80, preserveAspectRatio=True, mask='auto')
    if os.path.exists(FOOTER):
        canvas.drawImage(FOOTER, 0, 0, width=width, preserveAspectRatio=True, mask='auto')
    
    # Page number
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
    
    # Use the new header/footer that correctly numbers the page
    doc.build(disclaimer_elements, onFirstPage=lambda c, d: disclaimer_header_footer(c, d, start_page_num), onLaterPages=lambda c, d: disclaimer_header_footer(c, d, start_page_num))
    
    buffer.seek(0)
    return buffer

# --- PDF Generator ---
def generate_pdf():
    # Perform calculations on a temporary copy to avoid state conflicts
    lumpsum_df_final = st.session_state.lumpsum_df.copy()
    sip_df_final = st.session_state.sip_df.copy()
    initial_stp_df_final = st.session_state.initial_stp_df.copy()
    final_stp_df_final = st.session_state.final_stp_df.copy()
    
    try:
        lumpsum_total = float(investment_amount.replace(",", "")) if investment_amount else 0
        sip_total = float(sip_amount.replace(",", "")) if sip_amount else 0
    except (ValueError, AttributeError):
        lumpsum_total = 0
        sip_total = 0

    if lumpsum_total > 0 and not lumpsum_df_final.empty:
        lumpsum_df_final['Amount'] = pd.to_numeric(lumpsum_df_final['Amount'], errors='coerce').fillna(0)
        lumpsum_df_final['Allocation (%)'] = (lumpsum_df_final['Amount'] / lumpsum_total) * 100

    if sip_total > 0 and not sip_df_final.empty:
        sip_df_final['Amount'] = pd.to_numeric(sip_df_final['Amount'], errors='coerce').fillna(0)
        sip_df_final['Allocation (%)'] = (sip_df_final['Amount'] / sip_total) * 100

    if lumpsum_total > 0 and not initial_stp_df_final.empty:
        initial_stp_df_final['Amount'] = pd.to_numeric(initial_stp_df_final['Amount'], errors='coerce').fillna(0)
        initial_stp_df_final['Allocation (%)'] = (initial_stp_df_final['Amount'] / lumpsum_total) * 100

    if lumpsum_total > 0 and not final_stp_df_final.empty:
        final_stp_df_final['Amount'] = pd.to_numeric(final_stp_df_final['Amount'], errors='coerce').fillna(0)
        final_stp_df_final['Allocation (%)'] = (final_stp_df_final['Amount'] / lumpsum_total) * 100

    # Generate the main PDF content
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

    tables = []
    if include_lumpsum and not lumpsum_df_final.empty:
        tables.append(("Lumpsum Allocation", lumpsum_df_final))
    if include_sip and not sip_df_final.empty:
        tables.append(("SIP Allocation", sip_df_final))
    if include_fund_perf and not st.session_state.fund_perf_df.empty:
        tables.append(("Fund Performance", st.session_state.fund_perf_df))
    if include_initial_stp and not initial_stp_df_final.empty:
        tables.append(("Initial Investment Allocation", initial_stp_df_final))
    if include_final_stp and not final_stp_df_final.empty:
        tables.append(("Final Portfolio Allocation", final_stp_df_final))

    # Add tables to the PDF
    for title, df in tables:
        elements += [
            Spacer(1, 0.5*cm),
            KeepTogether(
                [
                    Paragraph(f"<b>{title}</b>", styles['Heading4']),
                    fund_performance_table(df) if "Fund Performance" in title else dataframe_to_table(df)
                ]
            )
        ]

    # Add factsheet links
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
    
    # Generate the disclaimer PDF
    disclaimer_buffer = generate_disclaimer_pdf(len(main_doc.pages))
    
    # Merge the two PDFs
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
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name=f"Investment_Sheet - {client_name}.pdf",
                mime="application/pdf"
            )
