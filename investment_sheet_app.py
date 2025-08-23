import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os
from PyPDF2 import PdfMerger 
from reportlab.platypus import KeepTogether
from reportlab.lib.enums import TA_LEFT
from datetime import datetime

# Static assets
LOGO = "D:/Sahayak essentials/Investment Sheet/static/logo.png"
FOOTER = "D:/Sahayak essentials/Investment Sheet/static/footer.png"

st.set_page_config(page_title="PDF Document Generator", layout="centered")

# Initialize session state
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = None

# Register Unicode font for proper character display
try:
    # Try to register a Unicode font (place NotoSans-Regular.ttf in your project directory)
    pdfmetrics.registerFont(TTFont('NotoSans', 'NotoSans-Regular.ttf'))
    UNICODE_FONT = 'NotoSans'
except:
    # Fallback to Helvetica if Unicode font not available
    UNICODE_FONT = 'Helvetica'

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

# --- Indian Number Formatting Function ---
def format_indian_number(amount):
    """Convert number to Indian comma format (1,00,000.00) with 2 decimal places"""
    try:
        num = float(amount)
    except:
        return "0.00"
    
    # Format with 2 decimal places
    formatted = f"{abs(num):.2f}"
    
    # Split integer and decimal parts
    if '.' in formatted:
        integer_part, decimal_part = formatted.split('.')
    else:
        integer_part, decimal_part = formatted, "00"
    
    # Apply Indian comma formatting to integer part
    if len(integer_part) <= 3:
        formatted_integer = integer_part
    else:
        # Take the last 3 digits
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        
        # Add commas every 2 digits for the remaining part (from right)
        formatted_remaining = ""
        while len(remaining) > 2:
            formatted_remaining = "," + remaining[-2:] + formatted_remaining
            remaining = remaining[:-2]
        
        if remaining:
            formatted_remaining = remaining + formatted_remaining
        
        formatted_integer = formatted_remaining + "," + last_three
    
    # Combine integer and decimal parts
    result = formatted_integer + "." + decimal_part
    
    # Add negative sign if needed
    if num < 0:
        result = "-" + result
    
    return result

# --- Financial Goal Planner Helper Functions ---
def calculate_future_value(present_value, inflation_rate, years):
    """Calculate future value with inflation"""
    return present_value * ((1 + inflation_rate/100) ** years)

def calculate_sip_amount(future_value, years, expected_return, existing_assets=0):
    """Calculate required SIP amount"""
    deficit = future_value - existing_assets
    if deficit <= 0:
        return 0
    
    monthly_rate = expected_return / 100 / 12
    months = years * 12
    
    if monthly_rate == 0:
        return deficit / months
    
    sip_amount = deficit * monthly_rate / (((1 + monthly_rate) ** months) - 1)
    return sip_amount

def calculate_lumpsum_amount(future_value, years, expected_return, existing_assets=0):
    """Calculate required lumpsum amount"""
    deficit = future_value - existing_assets
    if deficit <= 0:
        return 0
    
    annual_rate = expected_return / 100
    lumpsum = deficit / ((1 + annual_rate) ** years)
    return lumpsum

def calculate_stepup_sip(base_sip, stepup_rate=10):
    """Calculate step-up SIP amount"""
    return base_sip * (1 - stepup_rate/100)

def calculate_retirement_corpus(monthly_expenses, retirement_years, inflation_rate, tax_rate, investment_return):
    """Calculate corpus needed for retirement expenses"""
    annual_expenses = monthly_expenses * 12
    real_return = ((1 + investment_return/100) / (1 + inflation_rate/100)) - 1
    real_return_tax_adjusted = real_return * (1 - tax_rate/100)
    
    if real_return_tax_adjusted <= 0:
        return annual_expenses * retirement_years
    
    corpus = annual_expenses * (1 - (1 + real_return_tax_adjusted)**(-retirement_years)) / real_return_tax_adjusted
    return corpus

# --- Common PDF Helper Functions ---
def header_footer_with_logos(canvas, doc):
    canvas.saveState()
    width, height = A4
    
    # Logo at top - PROPERLY CENTERED
    if os.path.exists(LOGO):
        try:
            logo_width = 250
            logo_height = 150
            logo_x = (width - logo_width) / 2
            logo_y = height - 160
            
            canvas.drawImage(LOGO, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            canvas.setFont('Helvetica-Bold', 14)
            canvas.drawCentredString(width/2.0, height-50, "SAHAYAK ASSOCIATES")
    else:
        canvas.setFont('Helvetica-Bold', 14)
        canvas.drawCentredString(width/2.0, height-50, "SAHAYAK ASSOCIATES")
    
    # Footer at bottom
    if os.path.exists(FOOTER):
        try:
            footer_height = 80
            canvas.drawImage(FOOTER, 0, 0, width=width, height=footer_height, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            canvas.setFont('Helvetica', 9)
            canvas.drawCentredString(width/2.0, 30, "Contact: 91-9872804694 | www.sahayakassociates.com")
    else:
        canvas.setFont('Helvetica', 9)
        canvas.drawCentredString(width/2.0, 30, "Contact: 91-9872804694 | www.sahayakassociates.com")
        
    # Page number
    page_number_text = "Page %d" % doc.page
    canvas.setFont('Helvetica', 9)
    canvas.drawCentredString(width/2.0, 90, page_number_text)
    
    canvas.restoreState()

def dataframe_to_table(df):
    df = df.fillna('-')
    for col in df.columns:
        if df[col].dtype == float:
            df[col] = df[col].apply(lambda x: format_indian_number(x) if pd.notna(x) and x != '-' else '-')

    styles = getSampleStyleSheet()
    cell_style = ParagraphStyle(name='TableCell', parent=styles['Normal'], fontSize=9, leading=10, wordWrap='CJK', fontName=UNICODE_FONT)

    header_data = [Paragraph(col_name, cell_style) for col_name in df.columns]
    
    table_data = []
    for index, row in df.iterrows():
        row_data = []
        for item in row:
            if 'Amount' in str(item) or (isinstance(item, (int, float)) and item > 999):
                formatted_item = format_indian_number(item)
                row_data.append(Paragraph(f"Rs.{formatted_item}", cell_style))
            else:
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
    cell_style = ParagraphStyle(name='FundPerfCell', parent=styles['Normal'], fontSize=9, leading=10, wordWrap='CJK', fontName=UNICODE_FONT)
    
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
            
        if st.button("🎯 Financial Goal Planner", use_container_width=True, type="primary"):
            st.session_state.app_mode = "goal_planner"
            st.rerun()
    
    with col2:
        if st.button("📝 Minutes of Meeting", use_container_width=True, type="primary"):
            st.session_state.app_mode = "mom"
            st.rerun()
            
        if st.button("✅ Meeting Checklist", use_container_width=True, disabled=True):
            st.info("Coming Soon!")
    
    st.markdown("---")
    st.markdown("**Note:** Meeting Checklist generator is currently under development.")

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
            spaceAfter=5,
            fontName=UNICODE_FONT
        )

        bullet_style = ParagraphStyle(
            name='BulletStyle',
            parent=styles['Normal'],
            leftIndent=20,
            firstLineIndent=-15,
            spaceBefore=0,
            leading=14,
            fontSize=10,
            alignment=TA_LEFT,
            fontName=UNICODE_FONT
        )

        heading_style = ParagraphStyle(name='HeadingLarge', fontSize=20, leading=24, alignment=1, spaceAfter=20, fontName=UNICODE_FONT)
        client_style = ParagraphStyle(name='ClientDetails', parent=styles['Normal'], spaceAfter=6, leading=14, fontName=UNICODE_FONT)
        note_style = ParagraphStyle(name='NoteStyle', fontSize=7, leading=10, fontName=UNICODE_FONT)

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
            try:
                amount_num = float(investment_amount.replace(',', '').replace('Rs.', '').replace('Rs.', '').strip())
                formatted_amount = format_indian_number(amount_num)
                investment_summary_parts.append(f"Rs.{formatted_amount} (Lumpsum)")
            except:
                investment_summary_parts.append(f"Rs.{investment_amount} (Lumpsum)")
                
        if sip_amount.strip():
            try:
                sip_num = float(sip_amount.replace(',', '').replace('Rs.', '').replace('Rs.', '').strip())
                formatted_sip = format_indian_number(sip_num)
                investment_summary_parts.append(f"Rs.{formatted_sip} (SIP)")
            except:
                investment_summary_parts.append(f"Rs.{sip_amount} (SIP)")

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

        elements.append(PageBreak())
        
        disclaimer_heading_style = ParagraphStyle(
            name='DisclaimerHeading', 
            fontSize=16, 
            leading=24, 
            alignment=1,
            spaceAfter=25, 
            fontName='Helvetica-Bold'
        )
        
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("DISCLAIMER", disclaimer_heading_style))
        
        disclaimer_style = ParagraphStyle(
            name='DisclaimerStyle', 
            parent=styles['Normal'], 
            fontSize=9, 
            leading=11,
            fontName=UNICODE_FONT
        )
        
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
    
    # --- PDF Generator for MoM ---
    def generate_mom_pdf():
        buffer = BytesIO()
        styles = getSampleStyleSheet()
        
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
            fontName=UNICODE_FONT
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
            fontName=UNICODE_FONT
        )
        
        centered_profile_style = ParagraphStyle(
            name='CenteredProfile',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=1,
            spaceAfter=20,
            spaceBefore=10,
            fontName=UNICODE_FONT
        )
        
        elements = []
        
        elements.append(Paragraph("Minutes of Meeting", heading_style))
        elements.append(Spacer(1, 15))
        
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
            ('BACKGROUND', (0,0), (0,-1), HexColor('#E6F3F8')),
        ]))
        
        elements.append(meeting_info_table)
        elements.append(Spacer(1, 20))
        
        profile_text = f"<b>Investment Horizon:</b> {investment_horizon_mom} &nbsp;&nbsp;&nbsp;&nbsp; <b>Risk Profile:</b> {risk_profile_mom}<br/><br/><b>Return Expectation:</b> {return_expectation_mom} &nbsp;&nbsp;&nbsp;&nbsp; <b>Awareness level:</b> {awareness_level}"
        elements.append(Paragraph(profile_text, centered_profile_style))
        
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
        
        elements.append(Paragraph("<b>A. Review of Asset Allocation</b>", section_heading_style))
        
        asset_alloc_data = [
            [Paragraph("<b>Investor Name</b>", info_table_style), Paragraph("<b>Current Asset Allocation</b>", info_table_style), "", ""],
            ["", Paragraph("<b>Equity</b>", info_table_style), Paragraph("<b>Debt</b>", info_table_style), Paragraph("<b>Total</b>", info_table_style)],
            [Paragraph(f"<b>{client_name_mom}</b>", info_table_style), Paragraph(f"<b>{current_equity:.2f}%</b>", info_table_style), Paragraph(f"<b>{current_debt:.2f}%</b>", info_table_style), Paragraph("<b>100%</b>", info_table_style)]
        ]
        
        asset_alloc_table = Table(asset_alloc_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
        asset_alloc_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('SPAN', (1,0), (3,0)),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('BACKGROUND', (0,0), (-1,1), HexColor('#E6F3F8')),
        ]))
        elements.append(asset_alloc_table)
        elements.append(Spacer(1, 20))
        
        if not investment_df.empty and not investment_df.dropna(how='all').empty:
            total_amount = investment_df["Amount (Rs.)"].sum()
            
            investment_table_data = []
            investment_table_data.append([
                Paragraph("<b>Sr. No.</b>", info_table_style),
                Paragraph("<b>Scheme Type</b>", info_table_style),
                Paragraph("<b>Scheme Name</b>", info_table_style),
                Paragraph("<b>Allocation (%)</b>", info_table_style),
                Paragraph("<b>Amount (Rs.)</b>", info_table_style)
            ])
            
            for index, row in investment_df.iterrows():
                if not pd.isna(row["Scheme Type"]) and row["Scheme Type"].strip():
                    amount_formatted = format_indian_number(row['Amount (Rs.)']) if pd.notna(row['Amount (Rs.)']) else "0.00"
                    
                    investment_table_data.append([
                        Paragraph(f"<b>{row['Sr. No.']}</b>", info_table_style),
                        Paragraph(f"<b>{row['Scheme Type']}</b>", info_table_style),
                        Paragraph(str(row['Scheme Name']), info_table_style),
                        Paragraph(f"{row['Allocation (%)']:.2f}" if pd.notna(row['Allocation (%)']) else "0.00", info_table_style),
                        Paragraph(f"Rs.{amount_formatted}", info_table_style)
                    ])
            
            total_formatted = format_indian_number(total_amount)
            investment_table_data.append([
                Paragraph("<b>Total</b>", info_table_style),
                "", "",
                Paragraph("<b>100.00</b>", info_table_style),
                Paragraph(f"<b>Rs.{total_formatted}</b>", info_table_style)
            ])
            
            investment_table = Table(investment_table_data, colWidths=[1.5*cm, 2.5*cm, 7*cm, 2.5*cm, 2.5*cm])
            investment_table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (0,0), (-1,0), 'CENTER'),
                ('ALIGN', (3,1), (4,-1), 'RIGHT'),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('BACKGROUND', (0,0), (-1,0), HexColor('#E6F3F8')),
                ('BACKGROUND', (0,-1), (-1,-1), HexColor('#E6F3F8')),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
            ]))
            
            investment_section = KeepTogether([
                Paragraph("<b>Further Action:</b>", normal_style),
                Paragraph("Detail of Investment is as mention below in chart:", normal_style),
                Spacer(1, 10),
                investment_table
            ])
            
            elements.append(investment_section)
            elements.append(Spacer(1, 20))
        
        if include_mom_fund_perf and mom_fund_perf is not None and not mom_fund_perf.empty:
            elements.append(PageBreak())
            elements.append(Paragraph("<b>Fund Performance of above funds are given below:</b>", section_heading_style))
            
            fund_perf_table_optimized = fund_performance_table(mom_fund_perf)
            elements.append(fund_perf_table_optimized)
            elements.append(Spacer(1, 20))
        
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
        
        elements.append(PageBreak())
        
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
        
        elements.append(PageBreak())
        
        disclaimer_heading_style = ParagraphStyle(
            name='DisclaimerHeading', 
            fontSize=16, 
            leading=20, 
            alignment=1,
            spaceAfter=25, 
            fontName='Helvetica-Bold'
        )
        
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("DISCLAIMER", disclaimer_heading_style))
        
        disclaimer_style = ParagraphStyle(
            name='DisclaimerStyle', 
            parent=styles['Normal'], 
            fontSize=9, 
            leading=12,
            fontName=UNICODE_FONT
        )
        
        disclaimer_paragraphs = [p.strip() for p in DISCLAIMER_TEXT.split('.') if p.strip()]
        for paragraph in disclaimer_paragraphs:
            if paragraph:
                elements.append(Paragraph(paragraph + ".", disclaimer_style))
                elements.append(Spacer(1, 6))

        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=cm, leftMargin=cm, topMargin=5*cm, bottomMargin=3*cm)
        doc.build(elements, onFirstPage=header_footer_with_logos, onLaterPages=header_footer_with_logos)
        
        buffer.seek(0)
        return buffer

    if st.button("Generate MoM PDF"):
        client_name_safe = (client_name_mom or "").strip()
        meeting_date_safe = (meeting_date or "").strip()
        
        if not client_name_safe or not meeting_date_safe:
            st.error("Please enter at least Client Name and Meeting Date & Time to generate the PDF.")
        else:
            pdf = generate_mom_pdf()
            st.success("Minutes of Meeting PDF generated successfully!")
            st.download_button("Download MoM PDF", data=pdf, file_name="Minutes_of_Meeting.pdf", mime="application/pdf")

# --- Financial Goal Planner Generator ---
def show_financial_goal_planner():
    if st.button("← Back to Main Menu", key="back_goal_planner"):
        st.session_state.app_mode = None
        st.rerun()
    
    st.title("🎯 Financial Goal Planner")
    
    # --- Client Information ---
    st.header("👤 Client Information")
    col1, col2 = st.columns(2)
    
    with col1:
        client_name_goal = st.text_input("Client Name (Mr./Ms.)", placeholder="Enter client name")
        current_age = st.number_input("Current Age", min_value=18, max_value=80, value=30)
        
    with col2:
        date_goal = st.text_input("Date", value=datetime.now().strftime("%d-%m-%Y"))
        risk_profile_goal = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"], key="goal_risk")
    
    # Auto-fill expected returns based on risk profile
    default_return = 8 if risk_profile_goal == "Conservative" else 10 if risk_profile_goal == "Moderate" else 12
    
    st.markdown("---")
    st.header("🎯 Financial Goals Configuration")
    
    # --- Goal 1: Education Goal ---
    with st.expander("🎓 Education Goal", expanded=False):
        education_enabled = st.checkbox("Enable Education Goal", key="enable_education")
        
        if education_enabled:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Child Details")
                edu_child_name = st.text_input("Child Name", key="edu_child", placeholder="Enter child's name")
                child_current_age = st.number_input("Child's Current Age", min_value=0, max_value=25, value=5, key="child_age")
                
                st.subheader("Goal Timeline")
                edu_graduation_age = st.number_input("Graduation Age", value=18, min_value=16, max_value=25, key="edu_grad_age")
                edu_postgrad_age = st.number_input("Post-Graduation Age", value=21, min_value=18, max_value=30, key="edu_postgrad_age")
                
            with col2:
                st.subheader("Financial Planning")
                edu_graduation_cost = st.number_input("Graduation Cost (Rs.)", value=1000000, min_value=0, key="edu_grad_cost", 
                                                    help="Total amount needed for graduation")
                edu_postgrad_cost = st.number_input("Post-Graduation Cost (Rs.)", value=1500000, min_value=0, key="edu_postgrad_cost",
                                                   help="Total amount needed for post-graduation")
                edu_existing_savings = st.number_input("Current Savings (Rs.)", value=0, min_value=0, key="edu_existing",
                                                     help="Amount already saved for education")
                
                st.subheader("Investment Parameters")
                edu_inflation = st.number_input("Education Inflation (%)", value=8.0, min_value=0.0, max_value=20.0, key="edu_inflation")
                edu_expected_return = st.number_input("Expected Return (%)", value=float(default_return), min_value=0.0, max_value=30.0, key="edu_return")
            
            # Display timeline with Indian formatting
            grad_years = max(0, edu_graduation_age - child_current_age)
            postgrad_years = max(0, edu_postgrad_age - child_current_age)
            
            if grad_years <= 0:
                st.warning("⚠️ Graduation age should be greater than child's current age")
            elif postgrad_years <= grad_years:
                st.warning("⚠️ Post-graduation age should be greater than graduation age")
            else:
                st.success(f"📅 **Timeline:** Graduation in {grad_years} years, Post-graduation in {postgrad_years} years")
                
                if edu_existing_savings > 0:
                    grad_progress = (edu_existing_savings / edu_graduation_cost) * 100 if edu_graduation_cost > 0 else 0
                    postgrad_progress = (edu_existing_savings / edu_postgrad_cost) * 100 if edu_postgrad_cost > 0 else 0
                    formatted_savings = format_indian_number(edu_existing_savings)
                    st.info(f"💰 **Current Savings:** Rs.{formatted_savings} | **Progress:** Graduation {grad_progress:.1f}%, Post-Graduation {postgrad_progress:.1f}%")
    
    # --- Goal 2: Marriage/Business Goal ---
    with st.expander("💒 Marriage/Business Goal", expanded=False):
        marriage_enabled = st.checkbox("Enable Marriage/Business Goal", key="enable_marriage")
        
        if marriage_enabled:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Goal Details")
                marriage_person_name = st.text_input("Person Name", key="marriage_person", placeholder="Enter person's name")
                marriage_age = st.number_input("Target Age", value=max(25, current_age + 1), min_value=current_age + 1, max_value=80, key="marriage_age")
                marriage_goal_amount = st.number_input("Goal Amount (Rs.)", value=2000000, min_value=0, key="marriage_amount",
                                                     help="Total amount needed")
                
            with col2:
                st.subheader("Current Progress & Planning")
                marriage_existing_savings = st.number_input("Current Savings (Rs.)", value=0, min_value=0, key="marriage_existing",
                                                          help="Amount already saved")
                marriage_inflation = st.number_input("Inflation Rate (%)", value=6.0, min_value=0.0, max_value=20.0, key="marriage_inflation")
                marriage_expected_return = st.number_input("Expected Return (%)", value=float(default_return), min_value=0.0, max_value=30.0, key="marriage_return")
            
            years_remaining = marriage_age - current_age
            progress = (marriage_existing_savings / marriage_goal_amount * 100) if marriage_goal_amount > 0 else 0
            
            formatted_target = format_indian_number(marriage_goal_amount)
            formatted_savings = format_indian_number(marriage_existing_savings)
            st.success(f"📅 **Timeline:** {years_remaining} years remaining | **Target:** Rs.{formatted_target} | **Saved:** Rs.{formatted_savings} ({progress:.1f}%)")
    
    # --- Goal 3: Emergency Corpus ---
    with st.expander("🚨 Emergency Corpus", expanded=False):
        emergency_enabled = st.checkbox("Enable Emergency Corpus", key="enable_emergency")
        
        if emergency_enabled:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Emergency Planning")
                emergency_goal_amount = st.number_input("Emergency Fund Amount (Rs.)", value=600000, min_value=0, key="emergency_amount",
                                                       help="Recommended: 6-12 months of expenses")
                emergency_age = st.number_input("Target Age", value=current_age + 2, min_value=current_age + 1, max_value=80, key="emergency_age")
                
            with col2:
                st.subheader("Current Status & Parameters")
                emergency_existing_savings = st.number_input("Current Emergency Fund (Rs.)", value=0, min_value=0, key="emergency_existing")
                emergency_inflation = st.number_input("Inflation Rate (%)", value=4.0, min_value=0.0, max_value=20.0, key="emergency_inflation")
                emergency_expected_return = st.number_input("Expected Return (%)", value=6.0, min_value=0.0, max_value=30.0, key="emergency_return")
            
            years_remaining = emergency_age - current_age
            progress = (emergency_existing_savings / emergency_goal_amount * 100) if emergency_goal_amount > 0 else 0
            
            formatted_target = format_indian_number(emergency_goal_amount)
            formatted_savings = format_indian_number(emergency_existing_savings)
            st.success(f"📅 **Timeline:** {years_remaining} years remaining | **Target:** Rs.{formatted_target} | **Saved:** Rs.{formatted_savings} ({progress:.1f}%)")
    
    # --- Goal 4: Retirement Corpus ---
    with st.expander("🏖️ Retirement Corpus", expanded=False):
        retirement_enabled = st.checkbox("Enable Retirement Corpus", key="enable_retirement")
        
        if retirement_enabled:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Retirement Planning")
                retirement_age = st.number_input("Retirement Age", value=max(60, current_age + 5), min_value=current_age + 5, max_value=80, key="retirement_age")
                retirement_goal_amount = st.number_input("Retirement Corpus (Rs.)", value=50000000, min_value=0, key="retirement_amount",
                                                        help="Target retirement corpus")
                
            with col2:
                st.subheader("Current Status & Parameters")
                retirement_existing_savings = st.number_input("Current Retirement Savings (Rs.)", value=0, min_value=0, key="retirement_existing")
                retirement_inflation = st.number_input("Inflation Rate (%)", value=6.0, min_value=0.0, max_value=20.0, key="retirement_inflation")
                retirement_expected_return = st.number_input("Expected Return (%)", value=float(default_return), min_value=0.0, max_value=30.0, key="retirement_return")
            
            years_remaining = retirement_age - current_age
            progress = (retirement_existing_savings / retirement_goal_amount * 100) if retirement_goal_amount > 0 else 0
            
            formatted_target = format_indian_number(retirement_goal_amount)
            formatted_savings = format_indian_number(retirement_existing_savings)
            st.success(f"📅 **Timeline:** {years_remaining} years remaining | **Target:** Rs.{formatted_target} | **Saved:** Rs.{formatted_savings} ({progress:.1f}%)")
    
    # --- Goal 5: Retirement Expenses ---
    with st.expander("💰 Retirement Monthly Expenses", expanded=False):
        retirement_expenses_enabled = st.checkbox("Enable Retirement Expenses Planning", key="enable_retirement_expenses")
        
        if retirement_expenses_enabled:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Current Lifestyle")
                current_monthly_expenses = st.number_input("Current Monthly Expenses (Rs.)", value=50000, min_value=0, key="current_expenses")
                retirement_age_exp = st.number_input("Retirement Age", value=max(60, current_age + 5), min_value=current_age + 5, max_value=80, key="retirement_age_exp")
                life_expectancy = st.number_input("Life Expectancy", value=80, min_value=retirement_age_exp + 5, max_value=100, key="life_expectancy")
                
            with col2:
                st.subheader("Planning Parameters")
                retirement_exp_existing_savings = st.number_input("Current Savings for Expenses (Rs.)", value=0, min_value=0, key="retirement_exp_existing")
                expense_drop_percent = st.number_input("Expense Reduction after Retirement (%)", value=20.0, min_value=0.0, max_value=50.0, key="expense_drop")
                tax_rate = st.number_input("Tax on Investment Income (%)", value=10.0, min_value=0.0, max_value=40.0, key="tax_rate")
                retirement_inflation_exp = st.number_input("Retirement Inflation (%)", value=4.0, min_value=0.0, max_value=20.0, key="retirement_inflation_exp")
                retirement_return_exp = st.number_input("Return during Retirement (%)", value=8.0, min_value=0.0, max_value=20.0, key="retirement_return_exp")
            
            years_to_retirement = retirement_age_exp - current_age
            post_retirement_years = life_expectancy - retirement_age_exp
            
            formatted_expenses = format_indian_number(current_monthly_expenses)
            formatted_savings = format_indian_number(retirement_exp_existing_savings)
            st.success(f"📅 **Timeline:** Retirement in {years_to_retirement} years | **Current Monthly Expenses:** Rs.{formatted_expenses} | **Current Savings:** Rs.{formatted_savings}")
    
    # --- Current Assets ---
    st.markdown("---")
    st.header("💼 Current Assets Summary")
    st.write("📝 Please provide details of your current general assets (separate from goal-specific savings above):")
    
    asset_data = {
        "Asset Class": ["PPF", "FDR/Bank Deposits", "Mutual Funds", "Direct Equity", "Real Estate", "Gold", "Others"],
        "Expected Returns (%)": [7.5, 6.0, 12.0, 15.0, 8.0, 6.0, 8.0],
        "Current Value (Rs.)": [0, 0, 0, 0, 0, 0, 0]
    }
    
    assets_df = st.data_editor(
        pd.DataFrame(asset_data),
        use_container_width=True,
        key="current_assets",
        column_config={
            "Asset Class": st.column_config.TextColumn("Asset Class", disabled=True),
            "Expected Returns (%)": st.column_config.NumberColumn("Expected Returns (%)", min_value=0.0, max_value=30.0, format="%.1f"),
            "Current Value (Rs.)": st.column_config.NumberColumn("Current Value (Rs.)", min_value=0, format="%d")
        }
    )
    
    total_assets = assets_df["Current Value (Rs.)"].sum()
    if total_assets > 0:
        formatted_total_assets = format_indian_number(total_assets)
        st.info(f"💰 **Total Current Assets:** Rs.{formatted_total_assets}")
    
    # --- Calculate Button ---
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate_button = st.button("🧮 Calculate Financial Goals", type="primary", use_container_width=True)
    
    # --- Calculations ---
    if calculate_button:
        enabled_goals = [education_enabled, marriage_enabled, emergency_enabled, retirement_enabled, retirement_expenses_enabled]
        
        if not any(enabled_goals):
            st.error("❌ Please enable at least one financial goal to calculate!")
            return
        
        if not client_name_goal.strip():
            st.error("❌ Please enter client name!")
            return
        
        st.success("✅ Calculating your financial goals...")
        
        st.markdown("---")
        st.header("📊 Financial Goal Analysis Results")
        
        goals_summary = []
        total_sip = 0
        total_stepup_sip = 0
        total_lumpsum = 0
        
        # Education Goal Calculations
        if education_enabled and edu_child_name.strip() and grad_years > 0:
            if grad_years > 0:
                grad_future_value = calculate_future_value(edu_graduation_cost, edu_inflation, grad_years)
                existing_grad_future_value = calculate_future_value(edu_existing_savings, edu_expected_return, grad_years)
                grad_deficit = max(0, grad_future_value - existing_grad_future_value)
                
                grad_sip = calculate_sip_amount(grad_deficit, grad_years, edu_expected_return, 0)
                grad_stepup_sip = calculate_stepup_sip(grad_sip)
                grad_lumpsum = calculate_lumpsum_amount(grad_deficit, grad_years, edu_expected_return, 0)
                grad_progress = (existing_grad_future_value / grad_future_value) * 100 if grad_future_value > 0 else 0
                
                goals_summary.append({
                    "Goal": f"Graduation of {edu_child_name} @ {edu_graduation_age}",
                    "Target Amount": f"Rs.{format_indian_number(edu_graduation_cost)}",
                    "Future Value Required": f"Rs.{format_indian_number(grad_future_value)}",
                    "Existing Progress": f"Rs.{format_indian_number(existing_grad_future_value)} ({grad_progress:.1f}%)",
                    "Deficit": f"Rs.{format_indian_number(grad_deficit)}",
                    "Years": grad_years,
                    "Monthly SIP": f"Rs.{format_indian_number(grad_sip)}",
                    "Step-up SIP": f"Rs.{format_indian_number(grad_stepup_sip)}",
                    "Lumpsum": f"Rs.{format_indian_number(grad_lumpsum)}",
                    "Assumptions": f"Return: {edu_expected_return}%, Inflation: {edu_inflation}%"
                })
                
                total_sip += grad_sip
                total_stepup_sip += grad_stepup_sip
                total_lumpsum += grad_lumpsum
            
            if postgrad_years > 0 and postgrad_years > grad_years:
                postgrad_future_value = calculate_future_value(edu_postgrad_cost, edu_inflation, postgrad_years)
                existing_postgrad_future_value = calculate_future_value(edu_existing_savings, edu_expected_return, postgrad_years)
                postgrad_deficit = max(0, postgrad_future_value - existing_postgrad_future_value)
                
                postgrad_sip = calculate_sip_amount(postgrad_deficit, postgrad_years, edu_expected_return, 0)
                postgrad_stepup_sip = calculate_stepup_sip(postgrad_sip)
                postgrad_lumpsum = calculate_lumpsum_amount(postgrad_deficit, postgrad_years, edu_expected_return, 0)
                postgrad_progress = (existing_postgrad_future_value / postgrad_future_value) * 100 if postgrad_future_value > 0 else 0
                
                goals_summary.append({
                    "Goal": f"Post-Graduation of {edu_child_name} @ {edu_postgrad_age}",
                    "Target Amount": f"Rs.{format_indian_number(edu_postgrad_cost)}",
                    "Future Value Required": f"Rs.{format_indian_number(postgrad_future_value)}",
                    "Existing Progress": f"Rs.{format_indian_number(existing_postgrad_future_value)} ({postgrad_progress:.1f}%)",
                    "Deficit": f"Rs.{format_indian_number(postgrad_deficit)}",
                    "Years": postgrad_years,
                    "Monthly SIP": f"Rs.{format_indian_number(postgrad_sip)}",
                    "Step-up SIP": f"Rs.{format_indian_number(postgrad_stepup_sip)}",
                    "Lumpsum": f"Rs.{format_indian_number(postgrad_lumpsum)}",
                    "Assumptions": f"Return: {edu_expected_return}%, Inflation: {edu_inflation}%"
                })
                
                total_sip += postgrad_sip
                total_stepup_sip += postgrad_stepup_sip
                total_lumpsum += postgrad_lumpsum
        
        # Marriage/Business Goal Calculations
        if marriage_enabled and marriage_person_name.strip():
            marriage_years = marriage_age - current_age
            if marriage_years > 0:
                marriage_future_value = calculate_future_value(marriage_goal_amount, marriage_inflation, marriage_years)
                existing_marriage_future_value = calculate_future_value(marriage_existing_savings, marriage_expected_return, marriage_years)
                marriage_deficit = max(0, marriage_future_value - existing_marriage_future_value)
                
                marriage_sip = calculate_sip_amount(marriage_deficit, marriage_years, marriage_expected_return, 0)
                marriage_stepup_sip = calculate_stepup_sip(marriage_sip)
                marriage_lumpsum = calculate_lumpsum_amount(marriage_deficit, marriage_years, marriage_expected_return, 0)
                marriage_progress = (existing_marriage_future_value / marriage_future_value) * 100 if marriage_future_value > 0 else 0
                
                goals_summary.append({
                    "Goal": f"Marriage/Business of {marriage_person_name} @ {marriage_age}",
                    "Target Amount": f"Rs.{format_indian_number(marriage_goal_amount)}",
                    "Future Value Required": f"Rs.{format_indian_number(marriage_future_value)}",
                    "Existing Progress": f"Rs.{format_indian_number(existing_marriage_future_value)} ({marriage_progress:.1f}%)",
                    "Deficit": f"Rs.{format_indian_number(marriage_deficit)}",
                    "Years": marriage_years,
                    "Monthly SIP": f"Rs.{format_indian_number(marriage_sip)}",
                    "Step-up SIP": f"Rs.{format_indian_number(marriage_stepup_sip)}",
                    "Lumpsum": f"Rs.{format_indian_number(marriage_lumpsum)}",
                    "Assumptions": f"Return: {marriage_expected_return}%, Inflation: {marriage_inflation}%"
                })
                
                total_sip += marriage_sip
                total_stepup_sip += marriage_stepup_sip
                total_lumpsum += marriage_lumpsum
        
        # Emergency Corpus Calculations
        if emergency_enabled:
            emergency_years = emergency_age - current_age
            if emergency_years > 0:
                emergency_future_value = calculate_future_value(emergency_goal_amount, emergency_inflation, emergency_years)
                existing_emergency_future_value = calculate_future_value(emergency_existing_savings, emergency_expected_return, emergency_years)
                emergency_deficit = max(0, emergency_future_value - existing_emergency_future_value)
                
                emergency_sip = calculate_sip_amount(emergency_deficit, emergency_years, emergency_expected_return, 0)
                emergency_stepup_sip = calculate_stepup_sip(emergency_sip)
                emergency_lumpsum = calculate_lumpsum_amount(emergency_deficit, emergency_years, emergency_expected_return, 0)
                emergency_progress = (existing_emergency_future_value / emergency_future_value) * 100 if emergency_future_value > 0 else 0
                
                goals_summary.append({
                    "Goal": f"Emergency Corpus @ {emergency_age}",
                    "Target Amount": f"Rs.{format_indian_number(emergency_goal_amount)}",
                    "Future Value Required": f"Rs.{format_indian_number(emergency_future_value)}",
                    "Existing Progress": f"Rs.{format_indian_number(existing_emergency_future_value)} ({emergency_progress:.1f}%)",
                    "Deficit": f"Rs.{format_indian_number(emergency_deficit)}",
                    "Years": emergency_years,
                    "Monthly SIP": f"Rs.{format_indian_number(emergency_sip)}",
                    "Step-up SIP": f"Rs.{format_indian_number(emergency_stepup_sip)}",
                    "Lumpsum": f"Rs.{format_indian_number(emergency_lumpsum)}",
                    "Assumptions": f"Return: {emergency_expected_return}%, Inflation: {emergency_inflation}%"
                })
                
                total_sip += emergency_sip
                total_stepup_sip += emergency_stepup_sip
                total_lumpsum += emergency_lumpsum
        
        # Retirement Corpus Calculations
        if retirement_enabled:
            retirement_years = retirement_age - current_age
            if retirement_years > 0:
                retirement_future_value = calculate_future_value(retirement_goal_amount, retirement_inflation, retirement_years)
                existing_retirement_future_value = calculate_future_value(retirement_existing_savings, retirement_expected_return, retirement_years)
                retirement_deficit = max(0, retirement_future_value - existing_retirement_future_value)
                
                retirement_sip = calculate_sip_amount(retirement_deficit, retirement_years, retirement_expected_return, 0)
                retirement_stepup_sip = calculate_stepup_sip(retirement_sip)
                retirement_lumpsum = calculate_lumpsum_amount(retirement_deficit, retirement_years, retirement_expected_return, 0)
                retirement_progress = (existing_retirement_future_value / retirement_future_value) * 100 if retirement_future_value > 0 else 0
                
                goals_summary.append({
                    "Goal": f"Retirement Corpus @ {retirement_age}",
                    "Target Amount": f"Rs.{format_indian_number(retirement_goal_amount)}",
                    "Future Value Required": f"Rs.{format_indian_number(retirement_future_value)}",
                    "Existing Progress": f"Rs.{format_indian_number(existing_retirement_future_value)} ({retirement_progress:.1f}%)",
                    "Deficit": f"Rs.{format_indian_number(retirement_deficit)}",
                    "Years": retirement_years,
                    "Monthly SIP": f"Rs.{format_indian_number(retirement_sip)}",
                    "Step-up SIP": f"Rs.{format_indian_number(retirement_stepup_sip)}",
                    "Lumpsum": f"Rs.{format_indian_number(retirement_lumpsum)}",
                    "Assumptions": f"Return: {retirement_expected_return}%, Inflation: {retirement_inflation}%"
                })
                
                total_sip += retirement_sip
                total_stepup_sip += retirement_stepup_sip
                total_lumpsum += retirement_lumpsum
        
        # Retirement Expenses Calculations
        if retirement_expenses_enabled:
            retirement_years = retirement_age_exp - current_age
            post_retirement_years = life_expectancy - retirement_age_exp
            
            if retirement_years > 0 and post_retirement_years > 0:
                future_monthly_expenses = calculate_future_value(current_monthly_expenses, retirement_inflation_exp, retirement_years)
                adjusted_monthly_expenses = future_monthly_expenses * (1 - expense_drop_percent/100)
                retirement_expense_corpus = calculate_retirement_corpus(
                    adjusted_monthly_expenses, post_retirement_years, 
                    retirement_inflation_exp, tax_rate, retirement_return_exp
                )
                
                existing_retirement_exp_future_value = calculate_future_value(retirement_exp_existing_savings, retirement_expected_return, retirement_years)
                retirement_exp_deficit = max(0, retirement_expense_corpus - existing_retirement_exp_future_value)
                
                retirement_exp_sip = calculate_sip_amount(retirement_exp_deficit, retirement_years, retirement_expected_return, 0)
                retirement_exp_stepup_sip = calculate_stepup_sip(retirement_exp_sip)
                retirement_exp_lumpsum = calculate_lumpsum_amount(retirement_exp_deficit, retirement_years, retirement_expected_return, 0)
                retirement_exp_progress = (existing_retirement_exp_future_value / retirement_expense_corpus) * 100 if retirement_expense_corpus > 0 else 0
                
                goals_summary.append({
                    "Goal": f"Retirement Expenses @ {retirement_age_exp}",
                    "Target Amount": f"Rs.{format_indian_number(current_monthly_expenses)}/month",
                    "Future Value Required": f"Rs.{format_indian_number(retirement_expense_corpus)}",
                    "Existing Progress": f"Rs.{format_indian_number(existing_retirement_exp_future_value)} ({retirement_exp_progress:.1f}%)",
                    "Deficit": f"Rs.{format_indian_number(retirement_exp_deficit)}",
                    "Years": retirement_years,
                    "Monthly SIP": f"Rs.{format_indian_number(retirement_exp_sip)}",
                    "Step-up SIP": f"Rs.{format_indian_number(retirement_exp_stepup_sip)}",
                    "Lumpsum": f"Rs.{format_indian_number(retirement_exp_lumpsum)}",
                    "Assumptions": f"Monthly expenses: Rs.{format_indian_number(adjusted_monthly_expenses)} at retirement"
                })
                
                total_sip += retirement_exp_sip
                total_stepup_sip += retirement_exp_stepup_sip
                total_lumpsum += retirement_exp_lumpsum
        
        # Display Results
        if goals_summary:
            # Add totals row with Indian formatting
            goals_summary.append({
                "Goal": "**TOTAL ADDITIONAL REQUIRED**",
                "Target Amount": "**-**",
                "Future Value Required": "**-**",
                "Existing Progress": "**-**",
                "Deficit": "**-**",
                "Years": "**-**",
                "Monthly SIP": f"**Rs.{format_indian_number(total_sip)}**",
                "Step-up SIP": f"**Rs.{format_indian_number(total_stepup_sip)}**",
                "Lumpsum": f"**Rs.{format_indian_number(total_lumpsum)}**",
                "Assumptions": "**Combined Additional Requirements**"
            })
            
            # Display table
            results_df = pd.DataFrame(goals_summary)
            st.dataframe(results_df, use_container_width=True, hide_index=True)
            
            # Key Insights with Indian formatting
            st.subheader("📈 Key Financial Insights")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label="Additional Monthly SIP Required",
                    value=f"Rs.{format_indian_number(total_sip)}",
                    help="Additional monthly SIP needed to achieve all goals"
                )
            with col2:
                st.metric(
                    label="Additional Step-up SIP Required", 
                    value=f"Rs.{format_indian_number(total_stepup_sip)}",
                    help="Step-up SIP with 10% annual increase"
                )
            with col3:
                st.metric(
                    label="Additional Lumpsum Required",
                    value=f"Rs.{format_indian_number(total_lumpsum)}",
                    help="One-time lumpsum investment needed"
                )
            
            # Investment Recommendation
            st.subheader("💡 Investment Recommendation")
            if risk_profile_goal == "Aggressive":
                st.info("**📊 Recommended Asset Allocation:** 70% Equity, 30% Debt\n\n✅ Higher growth potential for long-term goals\n\n⚠️ Higher volatility in short term")
            elif risk_profile_goal == "Moderate":
                st.info("**📊 Recommended Asset Allocation:** 60% Equity, 40% Debt\n\n✅ Balanced approach for steady growth\n\n✅ Moderate risk with reasonable returns")
            else:
                st.info("**📊 Recommended Asset Allocation:** 40% Equity, 60% Debt\n\n✅ Conservative approach with capital protection\n\n✅ Lower volatility and stable returns")
            
            # Progress Visualization with Custom Y-axis
            st.subheader("📊 Goal Progress Visualization")
            
            if len(goals_summary) > 1:
                chart_data = pd.DataFrame(goals_summary[:-1])
                
                def extract_percentage(progress_text):
                    if pd.isna(progress_text) or progress_text == '-':
                        return 0.0
                    import re
                    match = re.search(r'\((\d+\.?\d*)%\)', str(progress_text))
                    if match:
                        return float(match.group(1))
                    return 0.0
                
                chart_data['Progress_Percentage'] = chart_data['Existing Progress'].apply(extract_percentage)
                
                import matplotlib.pyplot as plt
                import numpy as np
                
                fig, ax = plt.subplots(figsize=(14, 8))
                
                bars = ax.bar(range(len(chart_data)), chart_data['Progress_Percentage'], 
                            color='#1f77b4', alpha=0.8, edgecolor='navy', linewidth=1.5)
                
                # Customize Y-axis to show 0-100 in increments of 10
                ax.set_yticks(np.arange(0, 101, 10))
                ax.set_ylim(0, 100)
                
                ax.set_xticks(range(len(chart_data)))
                ax.set_xticklabels([goal.replace(' @', '\n@') for goal in chart_data['Goal']], 
                                 rotation=45, ha='right', fontsize=10)
                
                ax.set_ylabel('Progress Completion (%)', fontsize=14, fontweight='bold')
                ax.set_xlabel('Financial Goals', fontsize=14, fontweight='bold')
                ax.set_title('Financial Goals Progress Visualization', fontsize=16, fontweight='bold', pad=20)
                
                # Add percentage labels on top of bars
                for i, (bar, percentage) in enumerate(zip(bars, chart_data['Progress_Percentage'])):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                            f'{percentage:.1f}%', ha='center', va='bottom', 
                            fontweight='bold', fontsize=11)
                
                ax.grid(axis='y', alpha=0.3, linestyle='--')
                ax.set_axisbelow(True)
                
                # Color bars based on progress
                for i, (bar, percentage) in enumerate(zip(bars, chart_data['Progress_Percentage'])):
                    if percentage >= 75:
                        bar.set_color('#28a745')  # Green for good progress
                    elif percentage >= 25:
                        bar.set_color('#ffc107')  # Yellow for moderate progress  
                    elif percentage > 0:
                        bar.set_color('#fd7e14')  # Orange for some progress
                    else:
                        bar.set_color('#dc3545')  # Red for no progress
                
                plt.tight_layout()
                st.pyplot(fig)
                
                st.caption("**Y-Axis:** Percentage of goal completed (0-100% in increments of 10)")
                st.caption("**X-Axis:** Financial Goals")
                st.caption("**Colors:** 🟢 75%+ (On Track) | 🟡 25-74% (In Progress) | 🟠 1-24% (Started) | 🔴 0% (Not Started)")
            
            # Store results for PDF generation
            st.session_state.goal_results = {
                'client_info': {
                    'name': client_name_goal,
                    'age': current_age,
                    'date': date_goal,
                    'risk_profile': risk_profile_goal
                },
                'goals_summary': goals_summary,
                'total_sip': total_sip,
                'total_stepup_sip': total_stepup_sip,
                'total_lumpsum': total_lumpsum,
                'assets_df': assets_df
            }
            
        else:
            st.warning("⚠️ No valid goals configured. Please check your goal settings and try again.")
    
    # PDF Generation
    def generate_goal_planner_pdf():
        if 'goal_results' not in st.session_state:
            return None
            
        buffer = BytesIO()
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            name='Title', fontSize=20, leading=24, alignment=1, 
            spaceAfter=20, fontName='Helvetica-Bold'
        )
        
        client_style = ParagraphStyle(
            name='Client', parent=styles['Normal'], fontSize=11, 
            leading=14, spaceAfter=8, fontName=UNICODE_FONT
        )
        
        section_style = ParagraphStyle(
            name='Section', fontSize=14, leading=18, spaceAfter=12, 
            spaceBefore=15, fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            name='Normal', parent=styles['Normal'], fontSize=10, 
            leading=12, fontName=UNICODE_FONT
        )
        
        elements = []
        results = st.session_state.goal_results
        
        elements.append(Paragraph("Financial Goal Planner Report", title_style))
        elements.append(Paragraph(f"Generated on: {results['client_info']['date']}", client_style))
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph("Client Information", section_style))
        elements.append(Paragraph(f"<b>Client Name:</b> {results['client_info']['name']}", client_style))
        elements.append(Paragraph(f"<b>Age:</b> {results['client_info']['age']} years", client_style))
        elements.append(Paragraph(f"<b>Risk Profile:</b> {results['client_info']['risk_profile']}", client_style))
        
        risk_profile = results['client_info']['risk_profile']
        if risk_profile == "Aggressive":
            recommendation = "70% Equity, 30% Debt - Higher growth potential"
        elif risk_profile == "Moderate":
            recommendation = "60% Equity, 40% Debt - Balanced approach"
        else:
            recommendation = "40% Equity, 60% Debt - Conservative approach"
        
        elements.append(Paragraph(f"<b>Recommended Asset Allocation:</b> {recommendation}", client_style))
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("Financial Goals Analysis", section_style))
        
        goals_data = results['goals_summary']
        if goals_data:
            table_data = [
                [Paragraph("<b>Goal</b>", normal_style),
                 Paragraph("<b>Target</b>", normal_style),
                 Paragraph("<b>Progress</b>", normal_style),
                 Paragraph("<b>Monthly SIP</b>", normal_style),
                 Paragraph("<b>Lumpsum</b>", normal_style)]
            ]
            
            for goal in goals_data[:-1]:
                table_data.append([
                    Paragraph(goal['Goal'], normal_style),
                    Paragraph(goal['Target Amount'], normal_style),
                    Paragraph(goal['Existing Progress'], normal_style),
                    Paragraph(goal['Monthly SIP'], normal_style),
                    Paragraph(goal['Lumpsum'], normal_style)
                ])
            
            goals_table = Table(table_data, colWidths=[5*cm, 2.5*cm, 3*cm, 2.5*cm, 2.5*cm])
            goals_table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('BACKGROUND', (0,0), (-1,0), HexColor('#E6F3F8')),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (0,0), (-1,0), 'CENTER'),
                ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 4),
                ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ]))
            
            elements.append(goals_table)
            elements.append(Spacer(1, 20))
            
            elements.append(Paragraph("Investment Summary", section_style))
            elements.append(Paragraph(f"<b>Total Monthly SIP Required:</b> Rs.{format_indian_number(results['total_sip'])}", client_style))
            elements.append(Paragraph(f"<b>Total Step-up SIP Required:</b> Rs.{format_indian_number(results['total_stepup_sip'])}", client_style))
            elements.append(Paragraph(f"<b>Total Lumpsum Required:</b> Rs.{format_indian_number(results['total_lumpsum'])}", client_style))
            
            # ADD CURRENT ASSETS SECTION
            elements.append(PageBreak())
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("Current Asset Summary", section_style))
            
            assets_df = results['assets_df']
            if not assets_df.empty:
                asset_table_data = [
                    [Paragraph("<b>Asset Class</b>", normal_style),
                     Paragraph("<b>Expected Returns (%)</b>", normal_style),
                     Paragraph("<b>Current Value (Rs.)</b>", normal_style)]
                ]
                
                total_assets = 0
                for _, row in assets_df.iterrows():
                    if row['Current Value (Rs.)'] > 0:
                        asset_table_data.append([
                            Paragraph(str(row['Asset Class']), normal_style),
                            Paragraph(f"{row['Expected Returns (%)']:.2f}", normal_style),
                            Paragraph(f"Rs.{format_indian_number(row['Current Value (Rs.)'])}", normal_style)
                        ])
                        total_assets += row['Current Value (Rs.)']
                
                if total_assets > 0:
                    asset_table_data.append([
                        Paragraph("<b>Total Assets</b>", normal_style),
                        Paragraph("<b>-</b>", normal_style),
                        Paragraph(f"<b>Rs.{format_indian_number(total_assets)}</b>", normal_style)
                    ])
                
                asset_table = Table(asset_table_data, colWidths=[6*cm, 4*cm, 4*cm])
                asset_table.setStyle(TableStyle([
                    ('GRID', (0,0), (-1,-1), 1, colors.black),
                    ('BACKGROUND', (0,0), (-1,0), HexColor('#E6F3F8')),
                    ('BACKGROUND', (0,-1), (-1,-1), HexColor('#E6F3F8')),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ALIGN', (0,0), (-1,0), 'CENTER'),
                    ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
                    ('FONTSIZE', (0,0), (-1,-1), 9),
                    ('LEFTPADDING', (0,0), (-1,-1), 5),
                    ('RIGHTPADDING', (0,0), (-1,-1), 5),
                ]))
                
                elements.append(asset_table)
            else:
                elements.append(Paragraph("No current assets specified.", normal_style))
            # ADD PROGRESS CHART SECTION
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("Goal Progress Visualization", section_style))

            # Generate progress chart
            if goals_data and len(goals_data) > 1:  # Exclude the totals row
                chart_goals = goals_data[:-1]  # Remove the totals row
                
                # Extract progress percentages from the data
                progress_data = []
                for goal in chart_goals:
                    progress_text = goal.get('Existing Progress', '0%')
                    # Extract percentage from text like "Rs.6,80,244.48 (26.9%)"
                    import re
                    match = re.search(r'\((\d+\.?\d*)%\)', str(progress_text))
                    if match:
                        percentage = float(match.group(1))
                    else:
                        percentage = 0.0
                    
                    progress_data.append({
                        'goal_name': goal['Goal'].replace(' @', '\n@'),  # Line break for better display
                        'percentage': percentage
                    })
                
                # Create chart using matplotlib
                import matplotlib as plt
                import matplotlib
                matplotlib.use('Agg')  # Use non-GUI backend
                
                fig, ax = plt.subplots(figsize=(12, 6))
                
                goals_list = [item['goal_name'] for item in progress_data]
                percentages = [item['percentage'] for item in progress_data]
                
                # Create bars with color coding
                bar_colors = []
                for percentage in percentages:
                    if percentage >= 75:
                        bar_colors.append('#28a745')  # Green for good progress
                    elif percentage >= 25:
                        bar_colors.append('#ffc107')  # Yellow for moderate progress
                    elif percentage > 0:
                        bar_colors.append('#fd7e14')  # Orange for some progress
                    else:
                        bar_colors.append('#dc3545')  # Red for no progress

                bars = ax.bar(range(len(goals_list)), percentages, color=bar_colors, alpha=0.8, edgecolor='navy', linewidth=1.5)
                
                # Customize the chart
                ax.set_ylim(0, 100)
                ax.set_yticks(range(0, 101, 10))
                ax.set_xticks(range(len(goals_list)))
                ax.set_xticklabels(goals_list, rotation=45, ha='right', fontsize=9)
                ax.set_ylabel('Progress Completion (%)', fontsize=12, fontweight='bold')
                ax.set_xlabel('Financial Goals', fontsize=12, fontweight='bold')
                ax.set_title('Financial Goals Progress Visualization', fontsize=14, fontweight='bold', pad=20)
                
                # Add percentage labels on top of bars
                for i, (bar, percentage) in enumerate(zip(bars, percentages)):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                            f'{percentage:.1f}%', ha='center', va='bottom', 
                            fontweight='bold', fontsize=10)
                
                # Add grid
                ax.grid(axis='y', alpha=0.3, linestyle='--')
                ax.set_axisbelow(True)
                
                plt.tight_layout()
                
                # Save chart as image and add to PDF
                chart_buffer = BytesIO()  # Remove the duplicate import above this line
                plt.savefig(chart_buffer, format='PNG', dpi=300, bbox_inches='tight')
                chart_buffer.seek(0)
                plt.close(fig)  # Close the figure to free memory
                
                # Add chart to PDF
                from reportlab.platypus import Image
                chart_image = Image(chart_buffer, width=16*cm, height=8*cm)
                elements.append(chart_image)
                
        elements.append(PageBreak())
        disclaimer_style = ParagraphStyle(
            name='Disclaimer', fontSize=16, leading=20, alignment=1, 
            spaceAfter=25, fontName='Helvetica-Bold'
        )
        
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("DISCLAIMER", disclaimer_style))
        
        disclaimer_text_style = ParagraphStyle(
            name='DisclaimerText', parent=styles['Normal'], fontSize=9, 
            leading=12, fontName=UNICODE_FONT
        )
        
        disclaimer_paragraphs = [p.strip() for p in DISCLAIMER_TEXT.split('.') if p.strip()]
        for paragraph in disclaimer_paragraphs:
            if paragraph:
                elements.append(Paragraph(paragraph + ".", disclaimer_text_style))
                elements.append(Spacer(1, 6))
        
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=cm, leftMargin=cm, 
                               topMargin=5*cm, bottomMargin=3*cm)
        doc.build(elements, onFirstPage=header_footer_with_logos, onLaterPages=header_footer_with_logos)
        
        buffer.seek(0)
        return buffer
        
    
    # PDF Generation Button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📄 Generate PDF Report", type="secondary", use_container_width=True):
            if 'goal_results' not in st.session_state:
                st.error("❌ Please calculate financial goals first!")
            elif not client_name_goal.strip():
                st.error("❌ Please enter client name to generate PDF!")
            else:
                with st.spinner("Generating your financial goal report..."):
                    pdf = generate_goal_planner_pdf()
                    if pdf:
                        st.success("✅ PDF Report generated successfully!")
                        st.download_button(
                            "📥 Download Financial Goal Report",
                            data=pdf,
                            file_name=f"Financial_Goal_Report_{client_name_goal.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    else:
                        st.error("❌ Failed to generate PDF. Please try again.")

# --- Main App Logic ---
def main():
    if st.session_state.app_mode is None:
        show_main_screen()
    elif st.session_state.app_mode == "investment":
        show_investment_sheet()
    elif st.session_state.app_mode == "mom":
        show_mom()
    elif st.session_state.app_mode == "goal_planner":
        show_financial_goal_planner()

if __name__ == "__main__":
    main()

