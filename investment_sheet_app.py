import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, FrameBreak, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm
from io import BytesIO
import os
from PyPDF2 import PdfMerger 
from reportlab.platypus import KeepTogether
from reportlab.lib.enums import TA_LEFT
from datetime import datetim

# Static assets
LOGO = "logo.png"
FOOTER = "footer.png"

st.set_page_config(page_title="PDF Document Generator", layout="centered")

# Initialize session state
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = None

# Common disclaimer text
DISCLAIMER_TEXT = """Any information provided by Sahayak & their associates does not constitute an investment advice, offer, invitation & inducement to invest in securities or other investments and Sahayak is not soliciting any action based on it. 
Keep in mind that investing involves risk. The value of your investment will fluctuate over time, and you may gain or lose money / original capital. 
Guidance provided by Sahayak is purely educational. Sahayak doesn't guarantee that the information disseminated herein would result in any monetary or financial gains or loss as the information is purely educational & based on past returns & performance. 
Past performance is not a guide for future performance. Future returns are not guaranteed, and loss of original capital may occur. 
Before acting on any information, investor should consider whether it is suitable for their particular circumstances and if necessary, seek professional investment advice from a Registered Investment Advisor. 
All investments especially mutual fund investments are subject to market risks. Kindly read the Offer Documents carefully before investing. 
Sahayak does not provide legal or tax advice. The information herein is general and educational in nature and should not be considered legal or tax advice.
Tax laws and regulations are complex and subject to change, which can materially impact investment results. 
Sahayak doesn't guarantee that the information provided herein is accurate, complete, or timely. 
Sahayak makes no warranties with regard to such information or results obtained by its use, and disclaim any liability arising out of your use of, or any tax position taken in reliance on such information. 
Sahayak is a distributor of financial products and NOT an investment advisor and NOT Authorized to provide any investment advice by SEBI. 
Sahayak Associates is an AMFI Registered Mutual Fund Distributor only."""

# --- Common PDF Helper Functions ---
def header_footer_with_logos(canvas, doc):
    canvas.saveState()
    width, height = A4  # A4 size is approximately 595 x 842 points
    
    # Logo at top - PROPERLY CENTERED
    if os.path.exists(LOGO):
        try:
            logo_width = 250  # Your actual logo width
            logo_height = 150  # Your actual logo height
            logo_x = (width - logo_width) / 2  # Center horizontally: (595 - 250) / 2 = 172.5
            logo_y = height - 160  # Position from top
            
            canvas.drawImage(LOGO, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            # Fallback text header if logo fails
            canvas.setFont('Helvetica-Bold', 14)
            canvas.drawCentredString(width/2.0, height-50, "SAHAYAK ASSOCIATES")
    else:
        # Fallback text header if logo doesn't exist
        canvas.setFont('Helvetica-Bold', 14)
        canvas.drawCentredString(width/2.0, height-50, "SAHAYAK ASSOCIATES")
    
    # Footer at bottom - CORRECTED positioning
    if os.path.exists(FOOTER):
        try:
            footer_height = 80
            canvas.drawImage(FOOTER, 0, 0, width=width, height=footer_height, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            # Fallback text footer if footer fails
            canvas.setFont('Helvetica', 9)
            canvas.drawCentredString(width/2.0, 30, "Contact: 91-9872804694 | www.sahayakassociates.com")
    else:
        # Fallback text footer if footer doesn't exist
        canvas.setFont('Helvetica', 9)
        canvas.drawCentredString(width/2.0, 30, "Contact: 91-9872804694 | www.sahayakassociates.com")
        
    # Page number positioned above footer
    page_number_text = "Page %d" % doc.page
    canvas.setFont('Helvetica', 9)
    canvas.drawCentredString(width/2.0, 90, page_number_text)
    
    canvas.restoreState()

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

# --- Main App Selection Screen ---
def show_main_screen():
    st.title("📄 PDF Document Generator")
    st.markdown("---")
    
    st.markdown("### Welcome! Please select the type of document you'd like to generate:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Investment Sheet", use_container_width=True, type="primary"):
            st.session_state.app_mode = "investment"
            st.rerun()
            
        if st.button("🎯 Financial Goal", use_container_width=True, disabled=True):
            st.info("Coming Soon!")
    
    with col2:
        if st.button("📝 Minutes of Meeting", use_container_width=True, type="primary"):
            st.session_state.app_mode = "mom"
            st.rerun()
            
        if st.button("✅ Meeting Checklist", use_container_width=True, disabled=True):
            st.info("Coming Soon!")
    
    st.markdown("---")
    st.markdown("**Note:** Financial Goal and Meeting Checklist generators are currently under development.")

# --- Investment Sheet Generator ---
def show_investment_sheet():
    if st.button("← Back to Main Menu", key="back_investment"):
        st.session_state.app_mode = None
        st.rerun()
    
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
    lumpsum_alloc = None
    if include_lumpsum:
        lumpsum_alloc = editable_table("Lumpsum Allocation", [{"Category": "Equity", "SubCategory": "Mid Cap", "Scheme Name": "HDFC Mid Cap Fund", "Allocation (%)": 50.00, "Amount": 100000.00}], key="lumpsum")

    include_sip = st.checkbox("Include SIP Allocation Table")
    sip_alloc = None
    if include_sip:
        sip_alloc = editable_table("SIP Allocation", [{"Category": "Equity", "SubCategory": "Small Cap", "Scheme Name": "SBI Small Cap Fund", "Allocation (%)": 50.00, "Amount": 5000.00}], key="sip")

    include_fund_perf = st.checkbox("Include Fund Performance Table")
    fund_perf = None
    if include_fund_perf:
        st.subheader("Fund Performance")
        fund_perf_data = [{"Scheme Name": "HDFC Mid Cap Fund ", "PE": 25.50, "SD": 15.00, "SR": 1.20, "Beta": 0.90, "Alpha": 1.50, "1Y": 12.30, "3Y": 15.60, "5Y": 17.80, "10Y": 19.20}]
        fund_perf = st.data_editor(pd.DataFrame(fund_perf_data).astype({col: float for col in fund_perf_data[0] if col != 'Scheme Name'}), num_rows="dynamic", use_container_width=True, key="fund_perf")

    include_initial_stp = st.checkbox("Include Initial Investment Table (STP Clients Only)")
    initial_alloc = None
    if include_initial_stp:
        initial_alloc = editable_table("Initial Investment Allocation", [], key="initial_stp")

    include_final_stp = st.checkbox("Include Final Portfolio Table (Post STP)")
    final_alloc = None
    if include_final_stp:
        final_alloc = editable_table("Final Portfolio Allocation", [], key="final_stp")

    st.markdown("### Fund Factsheet Links")
    factsheet_links = st.text_area("Enter links in the format:\nFund Name - Description | https://link.com", height=150)

    # --- PDF Generator for Investment Sheet ---
    def generate_investment_pdf():
        buffer = BytesIO()
        styles = getSampleStyleSheet()
        
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
        if include_lumpsum and lumpsum_alloc is not None and not lumpsum_alloc.empty and not lumpsum_alloc.dropna(how='all').empty:
            tables.append(("Lumpsum Allocation", lumpsum_alloc))
        if include_sip and sip_alloc is not None and not sip_alloc.empty and not sip_alloc.dropna(how='all').empty:
            tables.append(("SIP Allocation", sip_alloc))
        if include_fund_perf and fund_perf is not None and not fund_perf.empty and not fund_perf.dropna(how='all').empty:
            tables.append(("Fund Performance", fund_perf))
        if include_initial_stp and initial_alloc is not None and not initial_alloc.empty and not initial_alloc.dropna(how='all').empty:
            tables.append(("Initial Investment Allocation", initial_alloc))
        if include_final_stp and final_alloc is not None and not final_alloc.empty and not final_alloc.dropna(how='all').empty:
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
                    table_elements.append(note_paragraph)
                
                elements.append(KeepTogether(table_elements))
                elements.append(Spacer(1, 10))

        if factsheet_links.strip():
            elements.append(Paragraph("<b>Fund Factsheets</b>", styles['Heading4']))
            for line in factsheet_links.strip().splitlines():
                if "|" in line:
                    label, url = line.split("|", 1)
                    elements.append(
                        Paragraph(
                            f"{label.strip()}: <u><link href='{url.strip()}' color='blue'>{url.strip()}</link></u>",
                            link_container_style 
                        )
                    )
                else:
                    elements.append(Paragraph(line.strip(), styles['Normal']))

        elements.append(PageBreak())  # Force new page for disclaimer
        
        # CENTERED DISCLAIMER HEADING
        disclaimer_heading_style = ParagraphStyle(
            name='DisclaimerHeading', 
            fontSize=16, 
            leading=24, 
            alignment=1,  # Center alignment
            spaceAfter=25, 
            fontName='Helvetica-Bold'
        )
        
        elements.append(Spacer(1, 30))  # Extra space at top of page
        elements.append(Paragraph("DISCLAIMER", disclaimer_heading_style))
        
        # Disclaimer content
        disclaimer_style = ParagraphStyle(
            name='DisclaimerStyle', 
            parent=styles['Normal'], 
            fontSize=9, 
            leading=11,
        )
        
        # Split disclaimer into paragraphs for better formatting
        disclaimer_paragraphs = [p.strip() for p in DISCLAIMER_TEXT.split('.') if p.strip()]
        for paragraph in disclaimer_paragraphs:
            if paragraph:
                elements.append(Paragraph(paragraph + ".", disclaimer_style))
                elements.append(Spacer(1, 5))

        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=cm, leftMargin=cm, topMargin=5*cm, bottomMargin=3*cm)
        doc.build(elements, onFirstPage=header_footer_with_logos, onLaterPages=header_footer_with_logos)
        
        buffer.seek(0)
        return buffer

    if st.button("Generate PDF"):
        if not client_name.strip() or not report_date.strip():
            st.error("Please enter both Client Name and Date to generate the PDF.")
        else:
            pdf = generate_investment_pdf()
            st.success("PDF generated successfully!")
            st.download_button("Download PDF", data=pdf, file_name="Investment_Sheet.pdf", mime="application/pdf")

# --- Minutes of Meeting Generator ---
def show_mom():
    if st.button("← Back to Main Menu", key="back_mom"):
        st.session_state.app_mode = None
        st.rerun()
    
    st.title("Minutes of Meeting Generator")
    
    # --- Meeting Info ---
    st.header("Meeting Information")
    col1, col2 = st.columns(2)
    
    with col1:
        client_name_mom = st.text_input("Client Name (Mr./Mrs.)")
        meeting_organizer = st.text_input("Meeting Organizer", value="Mr. Puneet Kohli")
        meeting_date = st.text_input("Meeting Date & Time", placeholder="2nd March & 12:10 P.M.")
        meeting_location = st.text_input("Meeting Location", placeholder="Chandigarh")
        
    with col2:
        minutes_drafted_date = st.text_input("Minutes Drafted Date", placeholder="7th March, 2022")
        investment_horizon_mom = st.selectbox("Investment Horizon", ["Short Term", "Medium Term", "Long Term"], key="mom_horizon")
        risk_profile_mom = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"], key="mom_risk")
        awareness_level = st.selectbox("Awareness Level", ["HIGH", "MEDIUM", "LOW"])
    
    # Auto-fill return expectation based on risk profile
    default_return_mom = ""
    if risk_profile_mom == "Aggressive":
        default_return_mom = "12% - 15% CAGR"
    elif risk_profile_mom == "Moderate":
        default_return_mom = "10% - 12% CAGR"
    elif risk_profile_mom == "Conservative":
        default_return_mom = "8% - 10% CAGR"
        
    return_expectation_mom = st.text_input("Return Expectation", value=default_return_mom)
    
    # --- Brief Description/Agenda ---
    st.header("Meeting Agenda")
    agenda_items = st.text_area("Brief Description/Agenda", 
                               value="- Review of Asset Allocation\n- Fund Review", 
                               height=100)
    
    # --- Current Asset Allocation ---
    st.header("Current Asset Allocation")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current_equity = st.number_input("Current Equity (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.01)
    with col2:
        current_debt = st.number_input("Current Debt (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.01)
    with col3:
        current_total = current_equity + current_debt
        st.text_input("Total (%)", value=f"{current_total:.2f}", disabled=True)
    
    # --- Investment Details ---
    st.header("Investment Details")
    
    default_investment_data = [
        {"Sr. No.": 1, "Scheme Type": "EQUITY", "Scheme Name": "", "Allocation (%)": 0.0, "Amount (Rs.)": 0.0},
        {"Sr. No.": 2, "Scheme Type": "DEBT", "Scheme Name": "", "Allocation (%)": 0.0, "Amount (Rs.)": 0.0},
        {"Sr. No.": 3, "Scheme Type": "HYBRID", "Scheme Name": "", "Allocation (%)": 0.0, "Amount (Rs.)": 0.0},
        {"Sr. No.": 4, "Scheme Type": "ARBITRAGE", "Scheme Name": "", "Allocation (%)": 0.0, "Amount (Rs.)": 0.0}
    ]
    
    investment_df = st.data_editor(
        pd.DataFrame(default_investment_data),
        num_rows="dynamic",
        use_container_width=True,
        key="mom_investment"
    )
    
    # --- Fund Performance ---
    include_mom_fund_perf = st.checkbox("Include Fund Performance Table", key="mom_fund_perf_check")
    mom_fund_perf = None
    if include_mom_fund_perf:
        st.subheader("Fund Performance")
        mom_fund_perf_data = [{"Scheme Name": "", "PE": 0.0, "SD": 0.0, "SR": 0.0, "Beta": 0.0, "Alpha": 0.0, "1Y": 0.0, "3Y": 0.0, "5Y": 0.0, "10Y": 0.0}]
        mom_fund_perf = st.data_editor(
            pd.DataFrame(mom_fund_perf_data).astype({col: float for col in mom_fund_perf_data[0] if col != 'Scheme Name'}), 
            num_rows="dynamic", 
            use_container_width=True, 
            key="mom_fund_perf"
        )
    
    # --- Factsheet Links ---
    st.header("Fund Factsheets")
    mom_factsheet_links = st.text_area("Enter factsheet links in the format:\nFund Name - Description | https://link.com", 
                                      height=100, 
                                      key="mom_factsheets")
    
    # --- IMPROVED PDF Generator for MoM ---
    def generate_mom_pdf():
        buffer = BytesIO()
        styles = getSampleStyleSheet()
        
        # Enhanced Custom styles with better typography
        heading_style = ParagraphStyle(
            name='MoMHeading', 
            fontSize=18, 
            leading=22, 
            alignment=1, 
            spaceAfter=20, 
            fontName='Helvetica-Bold'
        )
        
        info_table_style = ParagraphStyle(
            name='InfoTable', 
            parent=styles['Normal'], 
            fontSize=10, 
            leading=14,
            fontName='Helvetica'
        )
        
        section_heading_style = ParagraphStyle(
            name='SectionHeading', 
            fontSize=12, 
            leading=16, 
            spaceAfter=12, 
            spaceBefore=8,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            name='MoMNormal', 
            parent=styles['Normal'], 
            fontSize=10, 
            leading=14,
            fontName='Helvetica'
        )
        
        # CENTERED PROFILE STYLE
        centered_profile_style = ParagraphStyle(
            name='CenteredProfile',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=1,  # Center alignment
            spaceAfter=20,
            spaceBefore=10,
            fontName='Helvetica'
        )
        
        elements = []
        
        # Title
        elements.append(Paragraph("Minutes of Meeting", heading_style))
        elements.append(Spacer(1, 15))
        
        # Meeting Info Table with blue headers
        meeting_info_data = [
            [Paragraph("<b>Meeting Title</b>", info_table_style), Paragraph(f"<b>Portfolio Review of {client_name_mom}</b>", info_table_style)],
            [Paragraph("<b>Meeting Organizer</b>", info_table_style), Paragraph(f"<b>{meeting_organizer}</b>", info_table_style)],
            [Paragraph("<b>Meeting Date & Time</b>", info_table_style), Paragraph(f"<b>{meeting_date}</b>", info_table_style)],
            [Paragraph("<b>Meeting Location</b>", info_table_style), Paragraph(f"<b>{meeting_location}</b>", info_table_style)],
            [Paragraph("<b>Minutes Drafted Date</b>", info_table_style), Paragraph(f"<b>{minutes_drafted_date}</b>", info_table_style)]
        ]
        
        meeting_info_table = Table(meeting_info_data, colWidths=[7.5*cm, 8.5*cm])
        meeting_info_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('BACKGROUND', (0,0), (0,-1), HexColor('#E6F3F8')),  # Blue background for headers
        ]))
        
        elements.append(meeting_info_table)
        elements.append(Spacer(1, 20))
        
        # CENTERED Investment Profile
        profile_text = f"<b>Investment Horizon:</b> {investment_horizon_mom} &nbsp;&nbsp;&nbsp;&nbsp; <b>Risk Profile:</b> {risk_profile_mom}<br/><br/><b>Return Expectation:</b> {return_expectation_mom} &nbsp;&nbsp;&nbsp;&nbsp; <b>Awareness level:</b> {awareness_level}"
        elements.append(Paragraph(profile_text, centered_profile_style))
        
        # Brief Description/Agenda
        elements.append(Paragraph("<b>Brief Description/Agenda</b>", section_heading_style))
        
        agenda_table_data = [[Paragraph(agenda_items.replace('\n', '<br/>'), normal_style)]]
        agenda_table = Table(agenda_table_data, colWidths=[16*cm])
        agenda_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        elements.append(agenda_table)
        elements.append(Spacer(1, 20))
        
        # Review of Asset Allocation
        elements.append(Paragraph("<b>A. Review of Asset Allocation</b>", section_heading_style))
        
        asset_alloc_data = [
            [Paragraph("<b>Investor Name</b>", info_table_style), Paragraph("<b>Current Asset Allocation</b>", info_table_style), "", ""],
            ["", Paragraph("<b>Equity</b>", info_table_style), Paragraph("<b>Debt</b>", info_table_style), Paragraph("<b>Total</b>", info_table_style)],
            [Paragraph(f"<b>{client_name_mom}</b>", info_table_style), Paragraph(f"<b>{current_equity:.2f}%</b>", info_table_style), Paragraph(f"<b>{current_debt:.2f}%</b>", info_table_style), Paragraph("<b>100%</b>", info_table_style)]
        ]
        
        asset_alloc_table = Table(asset_alloc_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
        asset_alloc_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('SPAN', (1,0), (3,0)),  # Span "Current Asset Allocation" across three columns
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('BACKGROUND', (0,0), (-1,1), HexColor('#E6F3F8')),  # Blue header background
        ]))
        elements.append(asset_alloc_table)
        elements.append(Spacer(1, 20))
        
        # Investment Details Table - Further Action text kept with table
        if not investment_df.empty and not investment_df.dropna(how='all').empty:
            total_amount = investment_df["Amount (Rs.)"].sum()
            
            # Create investment table with blue headers
            investment_table_data = []
            # Header
            investment_table_data.append([
                Paragraph("<b>Sr. No.</b>", info_table_style),
                Paragraph("<b>Scheme Type</b>", info_table_style),
                Paragraph("<b>Scheme Name</b>", info_table_style),
                Paragraph("<b>Allocation (%)</b>", info_table_style),
                Paragraph("<b>Amount (Rs.)</b>", info_table_style)
            ])
            
            # Data rows
            for index, row in investment_df.iterrows():
                if not pd.isna(row["Scheme Type"]) and row["Scheme Type"].strip():
                    investment_table_data.append([
                        Paragraph(f"<b>{row['Sr. No.']}</b>", info_table_style),
                        Paragraph(f"<b>{row['Scheme Type']}</b>", info_table_style),
                        Paragraph(str(row['Scheme Name']), info_table_style),
                        Paragraph(f"{row['Allocation (%)']:.2f}" if pd.notna(row['Allocation (%)']) else "0.00", info_table_style),
                        Paragraph(f"{row['Amount (Rs.)']:,.2f}" if pd.notna(row['Amount (Rs.)']) else "0.00", info_table_style)
                    ])
            
            # Total row
            investment_table_data.append([
                Paragraph("<b>Total</b>", info_table_style),
                "", "",
                Paragraph("<b>100</b>", info_table_style),
                Paragraph(f"<b>{total_amount:,.2f}</b>", info_table_style)
            ])
            
            # Fixed column widths with blue headers
            investment_table = Table(investment_table_data, colWidths=[1.5*cm, 2.5*cm, 7*cm, 2.5*cm, 2.5*cm])
            investment_table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (0,0), (-1,0), 'CENTER'),  # Center headers
                ('ALIGN', (3,1), (4,-1), 'RIGHT'),   # Right align numbers
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('BACKGROUND', (0,0), (-1,0), HexColor('#E6F3F8')),  # Blue header background
                ('BACKGROUND', (0,-1), (-1,-1), HexColor('#E6F3F8')),  # Blue total row background
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
            ]))
            
            # Keep the table together with the Further Action text
            investment_section = KeepTogether([
                Paragraph("<b>Further Action:</b>", normal_style),
                Paragraph("Detail of Investment is as mention below in chart:", normal_style),
                Spacer(1, 10),
                investment_table
            ])
            
            elements.append(investment_section)
            elements.append(Spacer(1, 20))
        
        # Fund Performance with same blue headers
        if include_mom_fund_perf and mom_fund_perf is not None and not mom_fund_perf.empty:
            elements.append(PageBreak())  # Move to new page for fund performance
            elements.append(Paragraph("<b>Fund Performance of above funds are given below:</b>", section_heading_style))
            
            fund_perf_table_optimized = fund_performance_table(mom_fund_perf)
            elements.append(fund_perf_table_optimized)
            elements.append(Spacer(1, 20))
        
        # Factsheets
        if mom_factsheet_links.strip():
            elements.append(Paragraph("<b>Factsheets of the above funds are given below:</b>", section_heading_style))
            for line in mom_factsheet_links.strip().splitlines():
                if "|" in line:
                    label, url = line.split("|", 1)
                    elements.append(
                        Paragraph(
                            f"{label.strip()}: <u><link href='{url.strip()}' color='blue'>{url.strip()}</link></u>",
                            normal_style
                        )
                    )
                else:
                    elements.append(Paragraph(line.strip(), normal_style))
            elements.append(Spacer(1, 20))
        
        # Force new page for closing
        elements.append(PageBreak())
        
        # Closing on separate page
        elements.append(Spacer(1, 50))
        elements.append(Paragraph("Please revert for any clarifications. Kindly approve the same so that we can initiate the transactions for your authorization.", normal_style))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("<b>Happy Investing!</b>", normal_style))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("<b>With Best Regards and Good Wishes,</b>", normal_style))
        elements.append(Paragraph("<b>For and on behalf of</b>", normal_style))
        elements.append(Paragraph("<b>Sahayak Associates,</b>", normal_style))
        elements.append(Paragraph("<b>Sandeep Sahni/Puneet Kohli</b>", normal_style))
        elements.append(Paragraph("<b>91-9872804694/91-9872804694</b>", normal_style))
        
        # Force new page for disclaimer
        elements.append(PageBreak())
        
        # CENTERED DISCLAIMER HEADING
        disclaimer_heading_style = ParagraphStyle(
            name='DisclaimerHeading', 
            fontSize=16, 
            leading=20, 
            alignment=1,  # Center alignment
            spaceAfter=25, 
            fontName='Helvetica-Bold'
        )
        
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("DISCLAIMER", disclaimer_heading_style))
        
        # Disclaimer content
        disclaimer_style = ParagraphStyle(
            name='DisclaimerStyle', 
            parent=styles['Normal'], 
            fontSize=9, 
            leading=12,
            fontName='Helvetica'
        )
        
        # Split disclaimer into paragraphs for better formatting
        disclaimer_paragraphs = [p.strip() for p in DISCLAIMER_TEXT.split('.') if p.strip()]
        for paragraph in disclaimer_paragraphs:
            if paragraph:
                elements.append(Paragraph(paragraph + ".", disclaimer_style))
                elements.append(Spacer(1, 6))

        # Adjusted margins to accommodate header/footer
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=cm, leftMargin=cm, topMargin=5*cm, bottomMargin=3*cm)
        doc.build(elements, onFirstPage=header_footer_with_logos, onLaterPages=header_footer_with_logos)
        
        buffer.seek(0)
        return buffer

    # FIXED VALIDATION SECTION
    if st.button("Generate MoM PDF"):
        # Safe validation to handle None values
        client_name_safe = (client_name_mom or "").strip()
        meeting_date_safe = (meeting_date or "").strip()
        
        if not client_name_safe or not meeting_date_safe:
            st.error("Please enter at least Client Name and Meeting Date & Time to generate the PDF.")
        else:
            pdf = generate_mom_pdf()
            st.success("Minutes of Meeting PDF generated successfully!")
            st.download_button("Download MoM PDF", data=pdf, file_name="Minutes_of_Meeting.pdf", mime="application/pdf")



# --- Main App Logic ---
def main():
    if st.session_state.app_mode is None:
        show_main_screen()
    elif st.session_state.app_mode == "investment":
        show_investment_sheet()
    elif st.session_state.app_mode == "mom":
        show_mom()

if __name__ == "__main__":
    main()
