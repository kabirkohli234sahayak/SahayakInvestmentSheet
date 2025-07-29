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
LOGO = "logo.png"
FOOTER = "footer.png"

st.set_page_config(page_title="Investment Sheet Generator", layout="centered")
st.title("Investment Sheet Generator")

# --- Client Info ---
st.header("Client Information")
client_name = st.text_input("Client Name")
report_date = st.text_input("Date (DD-MM-YYYY)")
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
• Balance amount of Rs. 28.00 lacs will be invested into Debt funds, we will start STP (Systematic Transfer Plan) of
 Rs. 3.50 lacs every fortnight or according to the market opportunities from Debt Funds to Equity Funds till August 2025.
This is an important point to note.
""", height=150)

# --- Tables ---
def editable_table(title, default_rows, key):
    st.subheader(title)
    df = pd.DataFrame(default_rows if default_rows else [{"Category": "", "SubCategory": "", "Scheme Name": "", "Allocation (%)": 0.0, "Amount": 0.0}])
    df = df.astype({"Allocation (%)": object, "Amount": object})
    return st.data_editor(df, num_rows="dynamic", use_container_width=True, key=key)

include_lumpsum = st.checkbox("Include Lumpsum Allocation Table")
if include_lumpsum:
    lumpsum_alloc = editable_table("Lumpsum Allocation", [{"Category": "Equity", "SubCategory": "Mid Cap", "Scheme Name": "HDFC Mid Cap Fund", "Allocation (%)": 50.00, "Amount": 100000.00}], key="lumpsum")

include_sip = st.checkbox("Include SIP Allocation Table")
if include_sip:
    sip_alloc = editable_table("SIP Allocation", [{"Category": "Equity", "SubCategory": "Small Cap", "Scheme Name": "SBI Small Cap Fund", "Allocation (%)": 50.00, "Amount": 5000.00}], key="sip")

include_fund_perf = st.checkbox("Include Fund Performance Table")
if include_fund_perf:
    st.subheader("Fund Performance")
    fund_perf_data = [{"Scheme Name": "HDFC Mid Cap Fund with a very long name that should wrap for better readability", "PE": 25.50, "SD": 15.00, "SR": 1.20, "Beta": 0.90, "Alpha": 1.50, "1Y": 12.30, "3Y": 15.60, "5Y": 17.80, "10Y": 19.20}]
    fund_perf = st.data_editor(pd.DataFrame(fund_perf_data).astype({col: float for col in fund_perf_data[0] if col != 'Scheme Name'}), num_rows="dynamic", use_container_width=True, key="fund_perf")

include_initial_stp = st.checkbox("Include Initial Investment Table (STP Clients Only)")
if include_initial_stp:
    initial_alloc = editable_table("Initial Investment Allocation", [], key="initial_stp")

include_final_stp = st.checkbox("Include Final Portfolio Table (Post STP)")
if include_final_stp:
    final_alloc = editable_table("Final Portfolio Allocation", [], key="final_stp")

st.markdown("### Fund Factsheet Links")
factsheet_links = st.text_area("Enter links in the format:\nFund Name - Description | https://link.com", height=150)

# --- PDF Helpers ---
def dataframe_to_table(df):
    df = df.fillna('-')
    for col in df.columns:
        if df[col].dtype == float:
            df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) and x != '-' else '-')

    styles = getSampleStyleSheet()
    cell_style = ParagraphStyle(name='TableCell', parent=styles['Normal'], fontSize=9, leading=10, wordWrap='CJK')

    header_data = [Paragraph(col_name, cell_style) for col_name in df.columns]
    
    table_data = []
    for index, row in df.iterrows():
        row_data = []
        for item in row:
            row_data.append(Paragraph(str(item), cell_style))
        table_data.append(row_data)

    data = [header_data] + table_data

    table = Table(data, colWidths=None, repeatRows=1) 
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), HexColor('#E6F3F8')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('ALIGN', (0,1), (-1,-1), 'LEFT'),
        ('ALIGN', (-2,1), (-1,-1), 'RIGHT'),
    ]))
    return table

def fund_performance_table(df):
    df = df.fillna('-')
    
    numerical_cols = ['PE', 'SD', 'SR', 'Beta', 'Alpha', '1Y', '3Y', '5Y', '10Y']
    for col in numerical_cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"{float(x):.2f}" if pd.notna(x) and x != '-' else '-')

    display_columns = ['Scheme Name', 'PE', 'SD', 'SR', 'Beta', 'Alpha', '1Y', '3Y', '5Y', '10Y']
    current_columns = df.columns.tolist()
    final_display_columns = [col for col in display_columns if col in current_columns]
    df_display = df.reindex(columns=final_display_columns)

    styles = getSampleStyleSheet()
    cell_style = ParagraphStyle(name='FundPerfCell', parent=styles['Normal'], fontSize=9, leading=10, wordWrap='CJK')
    
    header_row1_elements = []
    header_row2_elements = []

    if 'Scheme Name' in final_display_columns:
        header_row1_elements.append(Paragraph('', cell_style))
        header_row2_elements.append(Paragraph('Scheme Name', cell_style))
    
    ratio_cols = [col for col in ['PE', 'SD', 'SR', 'Beta', 'Alpha'] if col in final_display_columns]
    if ratio_cols:
        header_row1_elements.append(Paragraph('Ratios', cell_style))
        header_row1_elements.extend([Paragraph('', cell_style)] * (len(ratio_cols) - 1))
        header_row2_elements.extend([Paragraph(col, cell_style) for col in ratio_cols])
        
    return_cols = [col for col in ['1Y', '3Y', '5Y', '10Y'] if col in final_display_columns]
    if return_cols:
        header_row1_elements.append(Paragraph('Returns', cell_style))
        header_row1_elements.extend([Paragraph('', cell_style)] * (len(return_cols) - 1))
        header_row2_elements.extend([Paragraph(col, cell_style) for col in return_cols])

    table_data_rows = []
    for index, row in df_display.iterrows():
        row_data = []
        for item in row:
            row_data.append(Paragraph(str(item), cell_style))
        table_data_rows.append(row_data)

    data = [header_row1_elements, header_row2_elements] + table_data_rows

    table = Table(data, colWidths=None, repeatRows=2) 
    
    style_commands = [
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BACKGROUND', (0,0), (-1,1), HexColor('#E6F3F8')),
        ('LINEBELOW', (0,0), (-1,1), 1, colors.black),
        ('LINEABOVE', (0,0), (-1,0), 1, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,1), 'CENTER'),
    ]

    if 'PE' in final_display_columns and 'Alpha' in final_display_columns:
        pe_idx = final_display_columns.index('PE')
        alpha_idx = final_display_columns.index('Alpha')
        style_commands.append(('SPAN', (pe_idx, 0), (alpha_idx, 0)))

    if '1Y' in final_display_columns and '10Y' in final_display_columns:
        _1y_idx = final_display_columns.index('1Y')
        _10y_idx = final_display_columns.index('10Y')
        style_commands.append(('SPAN', (_1y_idx, 0), (_10y_idx, 0)))
        
    first_num_col_idx = -1
    for col_name in display_columns:
        if col_name in final_display_columns and col_name != 'Scheme Name':
            first_num_col_idx = final_display_columns.index(col_name)
            break
            
    if first_num_col_idx != -1:
        style_commands.append(('ALIGN', (first_num_col_idx, 2), (-1,-1), 'RIGHT'))


    table.setStyle(TableStyle(style_commands))
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
    
    # We will define a specific style for the actual link text itself
    link_text_style = ParagraphStyle(
        name='LinkText',
        parent=styles['Normal'],
        textColor=colors.blue, # Set text color to blue
        underline=1,          # Add underline (1 for True)
        fontSize=10 # Ensure consistency
    )

    # Define a style for the overall paragraph containing the link, if needed for layout
    link_container_style = ParagraphStyle(
        name='LinkContainer',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        name='BulletStyle',
        parent=styles['Normal'],
        leftIndent=20,
        firstLineIndent=-15,
        spaceBefore=0,
        leading=14,
        fontSize=10,
        alignment=TA_LEFT
    )

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
    ]

    investment_summary_parts = []
    if investment_amount.strip():
        investment_summary_parts.append(f"Rs. {investment_amount} (Lumpsum)")
    if sip_amount.strip():
        investment_summary_parts.append(f"Rs. {sip_amount} (SIP)")

    if investment_summary_parts:
        elements.append(Paragraph(f"<b>Investment Amount:</b> {', '.join(investment_summary_parts)}", client_style))
    
    elements.append(Spacer(1, 10))
    
    if include_strategy_note:
        elements.append(Paragraph("<b>Investment Strategy</b>", styles['Heading3']))
        
        strategy_lines = strategy_note.strip().split("• ")
        for i, line in enumerate(strategy_lines):
            if line.strip():
                if i == 0 and not line.strip().startswith("•"):
                    elements.append(Paragraph(line.strip(), styles['Normal']))
                else:
                    elements.append(Paragraph(f"• {line.strip()}", bullet_style))
        elements.append(Spacer(1, 10))

    tables = []
    if include_lumpsum and not lumpsum_alloc.empty and not lumpsum_alloc.dropna(how='all').empty:
        tables.append(("Lumpsum Allocation", lumpsum_alloc))
    if include_sip and not sip_alloc.empty and not sip_alloc.dropna(how='all').empty:
        tables.append(("SIP Allocation", sip_alloc))
    if include_fund_perf and not fund_perf.empty and not fund_perf.dropna(how='all').empty:
        tables.append(("Fund Performance", fund_perf))
    if include_initial_stp and not initial_alloc.empty and not initial_alloc.dropna(how='all').empty:
        tables.append(("Initial Investment Allocation", initial_alloc))
    if include_final_stp and not final_alloc.empty and not final_alloc.dropna(how='all').empty:
        tables.append(("Final Portfolio Allocation", final_alloc))
        
    for title, df in tables:
        if not df.empty and not df.dropna(how='all').empty:
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
                elements.append(note_paragraph)
            
            elements.append(KeepTogether(table_elements))
            elements.append(Spacer(1, 10))

    if factsheet_links.strip():
        elements.append(Paragraph("<b>Fund Factsheets</b>", styles['Heading4']))
        for line in factsheet_links.strip().splitlines():
            if "|" in line:
                label, url = line.split("|", 1)
                elements.append(
                    Paragraph(
                        f"{label.strip()}: <u><link href='{url.strip()}' color='blue' >{url.strip()}</link></u>",
                        link_container_style 
                    )
                )
            else:
                elements.append(Paragraph(line.strip(), styles['Normal']))

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

    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=cm, leftMargin=cm, topMargin=cm, bottomMargin=cm)
    doc.build(elements, onFirstPage=header_footer_with_logos, onLaterPages=header_footer_with_logos)
    
    buffer.seek(0)
    return buffer

if st.button("Generate PDF"):
    if not client_name.strip() or not report_date.strip():
        st.error("Please enter both Client Name and Date to generate the PDF.")
    else:
        pdf = generate_pdf()
        st.success("PDF generated successfully!")
        st.download_button("Download PDF", data=pdf, file_name="Investment_Sheet.pdf", mime="application/pdf")
