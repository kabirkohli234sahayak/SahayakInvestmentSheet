import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os
from reportlab.platypus import KeepTogether
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from datetime import datetime
from PIL import Image as PILImage
import matplotlib.pyplot as plt
import numpy as np
import math

# Static assets
LOGO = "D:\Sahayak essentials\Investment Sheet\static\logo.png"
FOOTER = "D:\Sahayak essentials\Investment Sheet\static\footer.png"

st.set_page_config(
    page_title="Sahayak Associates | Document Generator", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS with BLUE GRADIENT THEME
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    /* COMPLETE REMOVAL OF STREAMLIT ELEMENTS AND WHITE SPACE */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Remove all Streamlit header and toolbar space */
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stHeader"] {height: 0px !important; min-height: 0px !important; display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    
    /* Kill all padding/margin above the app */
    html, body {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .stApp {
        background: #fafafa;
        margin: 0 !important;
        padding: 0 !important;
        top: 0 !important;
    }
    
    .main > div {
        padding: 0 !important;
        margin: 0 !important;
        max-width: none;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .block-container {
        padding: 0rem 1rem !important;
        margin: 0 !important;
        max-width: none !important;
    }
    
    .element-container {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Target Streamlit's main content area */
    [data-testid="stAppViewContainer"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Aggressive fix for all content blocks */
    .css-1rs6os, .css-10trblm, .css-1kyxreq, .css-k1vhr4, .css-18e3th9, .css-1d391kg, .css-1v3fvcr,
    .css-1rs6os.edgvbvh3, .css-10trblm.e1nzilvr0, .css-1kyxreq.etr89bj2, .css-k1vhr4.egzxvld3 {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Main container styling */
    .main-container {
        background: #fafafa;
        min-height: 0vh;
        padding: 1rem 1rem 1rem 1rem;
        margin: 0 !important;
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0.5rem 0 1rem 0;
        padding: 0;
    }
    
    /* BLUE GRADIENT THEME THROUGHOUT */
    .goal-section {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .goal-section h2 {
        margin: 0 0 1rem 0;
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    .info-card {
        background: rgba(255,255,255,0.95);
        color: #333;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #4facfe;
    }
    
    .calculation-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Enhanced Form Styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 0.8rem;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #4facfe;
        outline: none;
        box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.1);
    }
    
    /* Enhanced Buttons with BLUE GRADIENT */
    .stButton > button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Calculate Button Special Styling */
    .calculate-button {
        text-align: center;
        margin: 2rem 0;
    }
    
    .calculate-button .stButton > button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        font-size: 1.1rem;
        padding: 1rem 2rem;
        border-radius: 50px;
    }
    
    /* Results Section with BLUE GRADIENT */
    .results-section {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        color: white;
    }
    
    .results-title {
        color: white;
        font-size: 1.8rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* Investment Recommendation with BLUE GRADIENT */
    .investment-recommendation {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    .investment-recommendation h3 {
        margin: 0 0 1rem 0;
        font-size: 1.2rem;
    }
    
    .recommendation-item {
        background: rgba(255,255,255,0.2);
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    /* Table Styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* Service Grid */
    .services-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .service-card {
        background: white;
        border: 1px solid #e8e8e8;
        border-radius: 6px;
        padding: 1rem;
        transition: all 0.2s ease;
    }
    
    .service-card:hover {
        border-color: #4facfe;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }
    
    .service-title {
        font-size: 1rem;
        font-weight: 500;
        color: #1a1a1a;
        margin: 0 0 0.5rem 0;
    }
    
    .service-description {
        font-size: 0.8rem;
        color: #666;
        line-height: 1.4;
        margin: 0 0 0.75rem 0;
    }
    
    .app-header {
        background: white;
        border: 1px solid #e8e8e8;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .app-title {
        font-size: 1.75rem;
        font-weight: 500;
        color: #1a1a1a;
        margin: 0 0 0.25rem 0;
        letter-spacing: -0.01em;
    }
    
    .app-subtitle {
        font-size: 0.875rem;
        color: #666;
        font-weight: 400;
        margin: 0;
    }
    
    /* Form Labels */
    .stTextInput > label,
    .stSelectbox > label,
    .stTextArea > label,
    .stNumberInput > label {
        font-weight: 500;
        color: #374151;
        font-size: 0.8rem;
        margin-bottom: 0.25rem !important;
        font-family: 'Inter', sans-serif;
    }
    
    .stTextInput, .stSelectbox, .stTextArea, .stNumberInput {
        margin-bottom: 0.5rem !important;
    }
    
    .stCheckbox {
        margin: 0.25rem 0 !important;
    }
    
    .stCheckbox > label {
        font-weight: 500;
        color: #374151;
        font-size: 0.8rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Alert Styling */
    .stInfo, .stSuccess, .stError, .stWarning {
        border-radius: 4px;
        border-left: 2px solid;
        padding: 0.5rem;
        margin: 0.5rem 0;
        font-size: 0.8rem;
    }
    
    .stInfo {
        background: #f0f8ff;
        border-left-color: #4facfe;
    }
    
    .stSuccess {
        background: #f0fff4;
        border-left-color: #22c55e;
    }
    
    .stError {
        background: #fff5f5;
        border-left-color: #ef4444;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.8rem !important;
        margin: 0.5rem 0 !important;
    }
    
    .stProgress > div > div {
        background: #4facfe;
        border-radius: 2px;
    }
    
    .app-footer {
        background: white;
        border: 1px solid #e8e8e8;
        border-radius: 6px;
        padding: 1rem;
        margin-top: 1rem;
        text-align: center;
    }
    
    .footer-text {
        color: #666;
        font-size: 0.75rem;
        margin: 0.125rem 0;
    }
    
    .back-button {
        margin-bottom: 0.75rem;
    }
    
    .row-widget {
        gap: 0.75rem !important;
    }
    
    div[data-testid="column"] {
        padding-left: 0.375rem !important;
        padding-right: 0.375rem !important;
    }
    
    .stMultiSelect {
        margin-bottom: 0.5rem !important;
    }
    
    .stSpinner {
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .stMarkdown {
        margin-bottom: 0 !important;
    }
    
    .stTabs {
        margin: 0.5rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = None

# Initialize calculations state
if 'calculations_done' not in st.session_state:
    st.session_state.calculations_done = False

# Initialize goal calculations
if 'goal_calculations' not in st.session_state:
    st.session_state.goal_calculations = {}

# Register Unicode font
try:
    pdfmetrics.registerFont(TTFont('NotoSans', 'NotoSans-Regular.ttf'))
    UNICODE_FONT = 'NotoSans'
except:
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

# --- UTILITY FUNCTIONS ---
def format_indian_number(amount):
    try:
        num = float(amount)
    except:
        return "0.00"
    
    formatted = f"{abs(num):.2f}"
    
    if '.' in formatted:
        integer_part, decimal_part = formatted.split('.')
    else:
        integer_part, decimal_part = formatted, "00"
    
    if len(integer_part) <= 3:
        formatted_integer = integer_part
    else:
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        
        formatted_remaining = ""
        while len(remaining) > 2:
            formatted_remaining = "," + remaining[-2:] + formatted_remaining
            remaining = remaining[:-2]
        
        if remaining:
            formatted_remaining = remaining + formatted_remaining
        
        formatted_integer = formatted_remaining + "," + last_three
    
    result = formatted_integer + "." + decimal_part
    
    if num < 0:
        result = "-" + result
    
    return result

def calculate_future_value(present_value, inflation_rate, years):
    return present_value * ((1 + inflation_rate/100) ** years)

def calculate_sip_amount(future_value, years, expected_return, existing_assets=0):
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
    deficit = future_value - existing_assets
    if deficit <= 0:
        return 0
    
    annual_rate = expected_return / 100
    lumpsum = deficit / ((1 + annual_rate) ** years)
    return lumpsum

def calculate_stepup_sip(base_sip, stepup_rate=10):
    return base_sip * (1 - stepup_rate/100)

def calculate_retirement_corpus(monthly_expenses, retirement_years, inflation_rate, tax_rate, investment_return):
    annual_expenses = monthly_expenses * 12
    
    real_return = ((1 + investment_return/100) / (1 + inflation_rate/100)) - 1
    
    real_return_tax_adjusted = real_return * (1 - tax_rate)
    
    if real_return_tax_adjusted <= 0:
        return annual_expenses * retirement_years
    
    corpus = annual_expenses * (1 - (1 + real_return_tax_adjusted)**(-retirement_years)) / real_return_tax_adjusted
    
    return corpus

def calculate_goal_progress(current_age, target_age, already_saved, required_sip, expected_return):
    progress = []
    years = list(range(current_age, target_age + 1))
    
    monthly_rate = expected_return / 100 / 12
    
    for year in years:
        months_elapsed = (year - current_age) * 12
        
        if months_elapsed == 0:
            progress_value = already_saved
        else:
            fv_saved = already_saved * ((1 + expected_return/100) ** (year - current_age))
            
            if required_sip > 0 and monthly_rate > 0:
                fv_sip = required_sip * ((((1 + monthly_rate) ** months_elapsed) - 1) / monthly_rate)
            else:
                fv_sip = required_sip * months_elapsed
            
            progress_value = fv_saved + fv_sip
        
        progress.append(progress_value)
    
    return years, progress

# --- PDF Helper Functions ---
def header_footer_with_logos(canvas, doc):
    canvas.saveState()
    width, height = A4
    
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

# --- UI Helper Functions ---
def show_header():
    """Properly sized and centered header"""
    try:
        logo = PILImage.open(LOGO)
        # Center the logo with controlled size
        col1, col2, col3 = st.columns([2.30, 2, 1])
        with col2:
            st.image(logo, width=215)  # Fixed width instead of use_column_width=True
    except:
        st.markdown("""
        <div class="app-header">
            <h1 class="app-title">SAHAYAK ASSOCIATES</h1>
            <p class="app-subtitle">Professional Financial Planning Tools</p>
        </div>
        """, unsafe_allow_html=True)

def show_back_button(key):
    """Clean back button"""
    st.markdown('<div class="back-button">', unsafe_allow_html=True)
    if st.button("← Back to Main Menu", key=key):
        st.session_state.app_mode = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- Main App Selection Screen ---
def show_main_screen():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    show_header()
    
    st.markdown("""
        <div class="app-header">
            <h1 class="app-title">SAHAYAK ASSOCIATES</h1>
            <p class="app-subtitle">Professional Financial Planning Tools</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="services-grid">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div class="service-card">
            <h3 class="service-title">Investment Planning</h3>
            <p class="service-description">Generate professional investment sheets with portfolio allocations and fund performance analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Investment Sheet Generator", key="investment_btn"):
            st.session_state.app_mode = "investment"
            st.rerun()
        
        st.markdown("""
        <div class="service-card">
            <h3 class="service-title">Goal Planning</h3>
            <p class="service-description">Comprehensive financial goal planning with SIP calculations and progress tracking.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Financial Goal Planner", key="goal_btn"):
            st.session_state.app_mode = "goal_planner"
            st.session_state.calculations_done = False
            st.rerun()
        
        # NEW MODULE - Add this card
        st.markdown("""
        <div class="service-card">
            <h3 class="service-title">Investment Decision Analysis</h3>
            <p class="service-description">Real-time comparison across asset classes (MF, Real Estate, Gold, FD) to make informed investment decisions.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Multi-Asset Decision Analyzer", key="decision_btn"):
            st.session_state.app_mode = "decision_analyzer"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="service-card">
            <h3 class="service-title">Meeting Documentation</h3>
            <p class="service-description">Create detailed meeting minutes with client information and investment details.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Minutes of Meeting Generator", key="mom_btn"):
            st.session_state.app_mode = "mom"
            st.rerun()
        
        st.markdown("""
        <div class="service-card">
            <h3 class="service-title">Meeting Preparation</h3>
            <p class="service-description">Customizable pre-meeting checklists to ensure comprehensive client discussions.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Meeting Checklist Generator", key="checklist_btn"):
            st.session_state.app_mode = "checklist"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="app-footer">
        <p class="footer-text"><strong>Sahayak Associates</strong> - AMFI Registered Mutual Fund Distributor</p>
        <p class="footer-text">Professional financial planning and investment advisory services</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)



# --- 1. Financial Goal Planner (COMPLETE) ---
def show_financial_goal_planner():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    show_header()
    show_back_button("back_goal_planner")
    
    # Title Section with BLUE GRADIENT
    st.markdown("""
    <div class="goal-section">
        <h2>Financial Goal Planner</h2>
        <p>Comprehensive financial goal planning with SIP calculations and progress tracking</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize current_assets if not already set
    if 'current_assets' not in st.session_state:
        st.session_state.current_assets = pd.DataFrame({
            'Asset Class': ['Equity', 'Debt', 'Gold', 'Real Estate', 'Others'],
            'Expected Returns (%)': [12.0, 7.0, 8.0, 10.0, 5.0],
            'Current Value (Rs.)': [0, 0, 0, 0, 0]
        })
    
    # Client Information Section
    st.markdown('<div class="info-card"><h3>👤 Client Information</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Name (Mr./Ms.)", placeholder="Enter client name")
        current_age = st.number_input("Current Age", value=30)
    
    with col2:
        date_field = st.text_input("Date", value=datetime.now().strftime("%d-%m-%Y"))
        risk_profile = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])
    
    # GOAL SELECTION SECTION
    st.markdown('<div class="info-card"><h3>Select Goals to Calculate</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        include_education = st.checkbox("🎓 Education Goal", value=True)
    with col2:
        include_marriage = st.checkbox("💍 Marriage/Business Goal", value=True)
    with col3:
        include_emergency = st.checkbox("🚨 Emergency Corpus", value=True)
    with col4:
        include_retirement = st.checkbox("🏖️ Retirement Corpus", value=True)
    
    # Financial Goals Configuration (Only show selected goals)
    st.markdown('<div class="info-card"><h3>🎯 Financial Goals Configuration</h3></div>', unsafe_allow_html=True)
    
    # Education Goal (only if selected)
    if include_education:
        with st.expander("🎓 Education Goal", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                edu_goal_name = st.text_input("Goal Name", value="Child Education", key="edu_goal_name")
                edu_current_age = st.number_input("Child's Current Age", min_value=0, max_value=25, value=5, key="edu_current_age")
            with col2:
                edu_target_age = st.number_input("Age when goal is needed", min_value=1, max_value=30, value=18, key="edu_target_age")
                edu_current_cost = st.number_input("Current Cost of Education (Rs.)", min_value=0, value=500000, key="edu_current_cost")
            with col3:
                edu_inflation = st.number_input("Education Inflation (%)", min_value=0.0, max_value=20.0, value=8.0, key="edu_inflation")
                edu_return = st.number_input("Expected Return (%)", min_value=0.0, max_value=30.0, value=12.0, key="edu_return")
            
            edu_already_saved = st.number_input("Amount Already Saved for this Goal (Rs.)", min_value=0, value=0, key="edu_already_saved")
    
    # Marriage Goal (only if selected)
    if include_marriage:
        with st.expander("💍 Marriage/Business Goal", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                marriage_goal_name = st.text_input("Goal Name", value="Marriage/Business", key="marriage_goal_name")
                marriage_target_age = st.number_input("Age when goal is needed", min_value=18, max_value=80, value=31, key="marriage_target_age")
            with col2:
                marriage_amount = st.number_input("Target Amount (Rs.)", min_value=0, value=2000000, key="marriage_amount")
                marriage_inflation = st.number_input("Inflation (%)", min_value=0.0, max_value=20.0, value=6.0, key="marriage_inflation")
            with col3:
                marriage_return = st.number_input("Expected Return (%)", min_value=0.0, max_value=30.0, value=10.0, key="marriage_return")
            
            marriage_already_saved = st.number_input("Amount Already Saved for this Goal (Rs.)", min_value=0, value=0, key="marriage_already_saved")
    
    # Emergency Goal (only if selected)
    if include_emergency:
        with st.expander("🚨 Emergency Corpus", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                emergency_months = st.number_input("Emergency Fund (Months of expenses)", min_value=3, max_value=24, value=6, key="emergency_months")
                monthly_expenses = st.number_input("Current Monthly Expenses (Rs.)", min_value=0, value=50000, key="monthly_expenses")
            with col2:
                emergency_return = st.number_input("Expected Return (%)", min_value=0.0, max_value=15.0, value=6.0, key="emergency_return")
            
            emergency_already_saved = st.number_input("Amount Already Saved for Emergency Fund (Rs.)", min_value=0, value=0, key="emergency_already_saved")
    
    # Retirement Goal (only if selected)
    if include_retirement:
        with st.expander("🏖️ Retirement Corpus", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                retirement_age = st.number_input("Retirement Age", min_value=40, max_value=80, value=60, key="retirement_age")
                retirement_years = st.number_input("Years in Retirement", min_value=10, max_value=40, value=25, key="retirement_years")
            with col2:
                retirement_monthly_exp = st.number_input("Monthly Expenses at Retirement (Rs.)", min_value=0, value=100000, key="retirement_monthly_exp")
                retirement_inflation = st.number_input("Inflation (%)", min_value=0.0, max_value=15.0, value=6.0, key="retirement_inflation")
            with col3:
                retirement_return = st.number_input("Expected Return (%)", min_value=0.0, max_value=20.0, value=8.0, key="retirement_return")
            
            retirement_already_saved = st.number_input("Amount Already Saved for Retirement (Rs.)", min_value=0, value=0, key="retirement_already_saved")
    
    # Current Assets Summary
    st.markdown('<div class="info-card"><h3>💼 Current Assets Summary</h3><p>Please provide details of your current general assets:</p></div>', unsafe_allow_html=True)
    
    # Assets table editor
    edited_assets = st.data_editor(
        st.session_state.current_assets,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Asset Class": st.column_config.TextColumn("Asset Class", disabled=True),
            "Expected Returns (%)": st.column_config.NumberColumn("Expected Returns (%)", min_value=0.0, max_value=30.0, step=0.1, format="%.1f"),
            "Current Value (Rs.)": st.column_config.NumberColumn("Current Value (Rs.)", min_value=0, step=1000, format="%d")
        }
    )
    st.session_state.current_assets = edited_assets
    
    # Calculate Button
    st.markdown('<div class="calculate-button">', unsafe_allow_html=True)
    if st.button("Calculate Selected Financial Goals"):
        with st.spinner("⚡ Calculating your selected financial goals..."):
            
            calculated_goals = []
            total_sip = 0
            total_stepup_sip = 0
            total_lumpsum = 0
            
            # Process ONLY selected goals
            
            # 1. Education Goal
            if include_education and edu_current_age < edu_target_age and edu_current_cost > 0:
                years_to_education = edu_target_age - edu_current_age
                education_future_value = calculate_future_value(edu_current_cost, edu_inflation, years_to_education)
                edu_required_sip = calculate_sip_amount(education_future_value, years_to_education, edu_return, edu_already_saved)
                edu_stepup_sip = calculate_stepup_sip(edu_required_sip, 10)
                edu_required_lumpsum = calculate_lumpsum_amount(education_future_value, years_to_education, edu_return, edu_already_saved)
                
                calculated_goals.append({
                    'Goal': f'{edu_goal_name}',
                    'Target Value': education_future_value,
                    'Already Saved': edu_already_saved,
                    'Progress': (edu_already_saved / education_future_value * 100) if education_future_value > 0 else 0,
                    'Deficit': max(0, education_future_value - edu_already_saved),
                    'Monthly SIP': edu_required_sip,
                    'Step-up SIP': edu_stepup_sip,
                    'Lumpsum': edu_required_lumpsum
                })
                
                total_sip += edu_required_sip
                total_stepup_sip += edu_stepup_sip
                total_lumpsum += edu_required_lumpsum
            
            # 2. Marriage Goal
            if include_marriage and marriage_target_age > current_age and marriage_amount > 0:
                years_to_marriage = marriage_target_age - current_age
                marriage_future_value = calculate_future_value(marriage_amount, marriage_inflation, years_to_marriage)
                marriage_required_sip = calculate_sip_amount(marriage_future_value, years_to_marriage, marriage_return, marriage_already_saved)
                marriage_stepup_sip = calculate_stepup_sip(marriage_required_sip, 10)
                marriage_required_lumpsum = calculate_lumpsum_amount(marriage_future_value, years_to_marriage, marriage_return, marriage_already_saved)
                
                calculated_goals.append({
                    'Goal': f'{marriage_goal_name}',
                    'Target Value': marriage_future_value,
                    'Already Saved': marriage_already_saved,
                    'Progress': (marriage_already_saved / marriage_future_value * 100) if marriage_future_value > 0 else 0,
                    'Deficit': max(0, marriage_future_value - marriage_already_saved),
                    'Monthly SIP': marriage_required_sip,
                    'Step-up SIP': marriage_stepup_sip,
                    'Lumpsum': marriage_required_lumpsum
                })
                
                total_sip += marriage_required_sip
                total_stepup_sip += marriage_stepup_sip
                total_lumpsum += marriage_required_lumpsum
            
            # 3. Emergency Goal
            if include_emergency and emergency_months > 0 and monthly_expenses > 0:
                emergency_target = emergency_months * monthly_expenses
                emergency_required_sip = calculate_sip_amount(emergency_target, 1, emergency_return, emergency_already_saved)
                emergency_stepup_sip = calculate_stepup_sip(emergency_required_sip, 10)
                emergency_required_lumpsum = calculate_lumpsum_amount(emergency_target, 1, emergency_return, emergency_already_saved)
                
                calculated_goals.append({
                    'Goal': 'Emergency Fund',
                    'Target Value': emergency_target,
                    'Already Saved': emergency_already_saved,
                    'Progress': (emergency_already_saved / emergency_target * 100) if emergency_target > 0 else 0,
                    'Deficit': max(0, emergency_target - emergency_already_saved),
                    'Monthly SIP': emergency_required_sip,
                    'Step-up SIP': emergency_stepup_sip,
                    'Lumpsum': emergency_required_lumpsum
                })
                
                total_sip += emergency_required_sip
                total_stepup_sip += emergency_stepup_sip
                total_lumpsum += emergency_required_lumpsum
            
            # 4. Retirement Goal
            if include_retirement and retirement_age > current_age and retirement_monthly_exp > 0:
                years_to_retirement = retirement_age - current_age
                retirement_corpus_needed = calculate_retirement_corpus(retirement_monthly_exp, retirement_years, retirement_inflation, 0.3, retirement_return)
                retirement_required_sip = calculate_sip_amount(retirement_corpus_needed, years_to_retirement, retirement_return, retirement_already_saved)
                retirement_stepup_sip = calculate_stepup_sip(retirement_required_sip, 10)
                retirement_required_lumpsum = calculate_lumpsum_amount(retirement_corpus_needed, years_to_retirement, retirement_return, retirement_already_saved)
                
                calculated_goals.append({
                    'Goal': 'Retirement Corpus',
                    'Target Value': retirement_corpus_needed,
                    'Already Saved': retirement_already_saved,
                    'Progress': (retirement_already_saved / retirement_corpus_needed * 100) if retirement_corpus_needed > 0 else 0,
                    'Deficit': max(0, retirement_corpus_needed - retirement_already_saved),
                    'Monthly SIP': retirement_required_sip,
                    'Step-up SIP': retirement_stepup_sip,
                    'Lumpsum': retirement_required_lumpsum
                })
                
                total_sip += retirement_required_sip
                total_stepup_sip += retirement_stepup_sip
                total_lumpsum += retirement_required_lumpsum
            
            # Store results with client information
            st.session_state.goal_calculations = {
                'calculated_goals': calculated_goals,
                'total_sip': total_sip,
                'total_stepup_sip': total_stepup_sip,
                'total_lumpsum': total_lumpsum,
                'client_name': client_name,
                'current_age': current_age,
                'date_field': date_field,
                'risk_profile': risk_profile,
                'edited_assets': edited_assets
            }
            
            st.session_state.calculations_done = True
            st.success(f"✅ Calculated {len(calculated_goals)} selected financial goals successfully!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display Results (only for selected goals)
    if st.session_state.get('calculations_done', False) and st.session_state.get('goal_calculations'):
        results = st.session_state.goal_calculations
        
        # Results Section
        st.markdown("""
        <div class="results-section">
            <div class="results-title">📈 Selected Goals Analysis Results</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create results DataFrame for selected goals
        results_data = []
        for goal in results['calculated_goals']:
            results_data.append({
                'Goal': goal['Goal'],
                'Target Value': f"Rs.{format_indian_number(goal['Target Value'])}",
                'Already Saved': f"Rs.{format_indian_number(goal['Already Saved'])}",
                'Progress': f"{goal['Progress']:.1f}%",
                'Deficit': f"Rs.{format_indian_number(goal['Deficit'])}",
                'Monthly SIP': f"Rs.{format_indian_number(goal['Monthly SIP'])}",
                'Step-up SIP': f"Rs.{format_indian_number(goal['Step-up SIP'])}",
                'Lumpsum': f"Rs.{format_indian_number(goal['Lumpsum'])}"
            })
        
        if results_data:
            results_df = pd.DataFrame(results_data)
            st.dataframe(results_df, use_container_width=True, hide_index=True)
        
        # Summary Metrics
        st.markdown('<div class="info-card"><h3>Combined Selected Goals Summary</h3></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Monthly SIP Required</div>
                <div class="metric-value">Rs.{format_indian_number(results['total_sip'])}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Step-up SIP Required</div>
                <div class="metric-value">Rs.{format_indian_number(results['total_stepup_sip'])}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Lumpsum Required</div>
                <div class="metric-value">Rs.{format_indian_number(results['total_lumpsum'])}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Progress Visualization for selected goals
        if results['calculated_goals']:
            st.markdown('<div class="calculation-card"><h3>Selected Goals Progress</h3></div>', unsafe_allow_html=True)
            
            fig, ax = plt.subplots(figsize=(12, 6))
            goal_names = [goal['Goal'] for goal in results['calculated_goals']]
            progress_values = [goal['Progress'] for goal in results['calculated_goals']]
            
            bars = ax.barh(goal_names, progress_values, color='#4facfe')
            ax.set_xlabel('Progress Completion (%)')
            ax.set_ylabel('Selected Financial Goals')
            ax.set_title('Current Progress Towards Selected Goals')
            ax.set_xlim(0, 100)
            
            for i, (bar, value) in enumerate(zip(bars, progress_values)):
                ax.text(value + 1, i, f'{value:.1f}%', va='center')
            
            ax.grid(True, alpha=0.3, axis='x')
            st.pyplot(fig)
            plt.close()
        
        # PDF Generation Button (ONLY shows after calculation)
        st.markdown('<div class="calculate-button">', unsafe_allow_html=True)
        if st.button("📄 Generate Financial Goal Report PDF"):
            if not client_name:
                st.error("Please enter a client name before generating the PDF.")
            elif not results.get('calculated_goals'):
                st.error("No goals were calculated. Please select and calculate goals first.")
            else:
                def generate_financial_goal_pdf():
                    buffer = BytesIO()
                    
                    # Create PDF document
                    styles = getSampleStyleSheet()
                    
                    # Define custom styles
                    heading_style = ParagraphStyle(
                        name='HeadingLarge', 
                        fontSize=20, 
                        leading=24, 
                        alignment=TA_CENTER,
                        spaceAfter=20, 
                        fontName=UNICODE_FONT,
                        textColor=colors.black
                    )
                    client_style = ParagraphStyle(
                        name='ClientDetails', 
                        parent=styles['Normal'], 
                        spaceAfter=6, 
                        leading=14, 
                        fontName=UNICODE_FONT,
                        fontSize=11
                    )
                    
                    subheading_style = ParagraphStyle(
                        name='SubHeading',
                        fontSize=14,
                        leading=18,
                        spaceAfter=10,
                        spaceBefore=15,
                        fontName='Helvetica-Bold',
                        textColor=colors.black
                    )

                    elements = []
                    
                    # Title
                    elements.append(Paragraph("Financial Goal Planner Report", heading_style))
                    elements.append(Paragraph(f"Generated on: {date_field}", client_style))
                    elements.append(Spacer(1, 20))
                    
                    # Client Information Section
                    elements.append(Paragraph("Client Information", subheading_style))
                    elements.append(Paragraph(f"<b>Client Name:</b> {client_name}", client_style))
                    elements.append(Paragraph(f"<b>Age:</b> {current_age} years", client_style))
                    elements.append(Paragraph(f"<b>Risk Profile:</b> {risk_profile}", client_style))
                    
                    # Asset allocation recommendation
                    asset_allocation = {"Conservative": "40% Equity, 60% Debt", "Moderate": "60% Equity, 40% Debt", "Aggressive": "80% Equity, 20% Debt"}[risk_profile]
                    elements.append(Paragraph(f"<b>Recommended Asset Allocation:</b> {asset_allocation} - {risk_profile} approach", client_style))
                    elements.append(Spacer(1, 20))
                    
                    # Financial Goals Analysis Section
                    elements.append(Paragraph("Financial Goals Analysis", subheading_style))

                    # Create table data for goals
                    if results['calculated_goals']:
                        table_data = [
                            ['Goal', 'Target', 'Progress', 'Monthly SIP', 'Lumpsum']
                        ]
                        
                        for goal in results['calculated_goals']:
                            table_data.append([
                                goal['Goal'],
                                f"Rs.{format_indian_number(goal['Target Value'])}",
                                f"Rs.{format_indian_number(goal['Already Saved'])} ({goal['Progress']:.1f}%)",
                                f"Rs.{format_indian_number(goal['Monthly SIP'])}",
                                f"Rs.{format_indian_number(goal['Lumpsum'])}"
                            ])
                        
                        # Create table with matching color scheme to Current Asset Summary
                        goal_table = Table(table_data, colWidths=[6*cm, 3.5*cm, 4*cm, 3.5*cm, 3.5*cm])
                        goal_table.setStyle(TableStyle([
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Matching grid
                            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#E6F3F8')),  # Matching header background (light blue)
                            # No body background (matches Current Asset Summary)
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Matching vertical alignment
                            ('LEFTPADDING', (0, 0), (-1, -1), 4),    # Matching padding
                            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),    # Center header
                            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),     # Left-align body
                            ('ALIGN', (-2, 1), (-1, -1), 'RIGHT'),   # Right-align numbers in body
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold header
                            ('FONTSIZE', (0, 0), (-1, 0), 10),       # Matching font sizes
                            ('FONTSIZE', (0, 1), (-1, -1), 9),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding for header
                        ]))
                        
                        elements.append(goal_table) 
                        elements.append(Spacer(1, 20))

                    
                    # Investment Summary Section
                    elements.append(Paragraph("Investment Summary", subheading_style))
                    elements.append(Paragraph(f"<b>Total Monthly SIP Required:</b> Rs.{format_indian_number(results['total_sip'])}", client_style))
                    elements.append(Paragraph(f"<b>Total Step-up SIP Required:</b> Rs.{format_indian_number(results['total_stepup_sip'])}", client_style))
                    elements.append(Paragraph(f"<b>Total Lumpsum Required:</b> Rs.{format_indian_number(results['total_lumpsum'])}", client_style))
                    elements.append(Spacer(1, 20))
                    
                    # Current Asset Summary Section
                    elements.append(PageBreak())
                    elements.append(Paragraph("Current Asset Summary", subheading_style))
                    assets_table = dataframe_to_table(results['edited_assets'])
                    elements.append(assets_table)
                    elements.append(Spacer(1, 20))
                    
                    # Goal Progress Visualization
                    elements.append(Paragraph("Goal Progress Visualization", subheading_style))
                    fig, ax = plt.subplots(figsize=(8, 4))  # Adjusted size for PDF
                    goal_names = [goal['Goal'] for goal in results['calculated_goals']]
                    progress_values = [goal['Progress'] for goal in results['calculated_goals']]
                    
                    bars = ax.barh(goal_names, progress_values, color='#4facfe')
                    ax.set_xlabel('Progress Completion (%)')
                    ax.set_ylabel('Selected Financial Goals')
                    ax.set_title('Current Progress Towards Selected Goals')
                    ax.set_xlim(0, 100)
                    
                    for i, (bar, value) in enumerate(zip(bars, progress_values)):
                        ax.text(value + 1, i, f'{value:.1f}%', va='center')
                    
                    ax.grid(True, alpha=0.3, axis='x')
                    
                    # Save figure to BytesIO
                    img_buffer = BytesIO()
                    plt.savefig(img_buffer, format='png', bbox_inches='tight')
                    plt.close(fig)
                    img_buffer.seek(0)
                    
                    # Insert image into PDF
                    img = Image(img_buffer, width=15*cm, height=10*cm)  # Adjust size as needed
                    elements.append(img)
                    elements.append(Spacer(1, 20))
                    
                    # Page break before disclaimer
                    elements.append(PageBreak())
                    
                    # Disclaimer Section
                    elements.append(Spacer(1, 30))
                    elements.append(Paragraph("DISCLAIMER", ParagraphStyle(
                        name='DisclaimerHeading', 
                        fontSize=16, 
                        leading=24, 
                        alignment=TA_CENTER,
                        spaceAfter=25, 
                        fontName='Helvetica-Bold'
                    )))
                    
                    disclaimer_style = ParagraphStyle(
                        name='DisclaimerStyle', 
                        parent=styles['Normal'], 
                        fontSize=9, 
                        leading=11,
                        fontName=UNICODE_FONT
                    )
                    
                    # Split disclaimer into paragraphs
                    disclaimer_paragraphs = [p.strip() for p in DISCLAIMER_TEXT.split('.') if p.strip()]
                    for paragraph in disclaimer_paragraphs:
                        if paragraph:
                            elements.append(Paragraph(paragraph + ".", disclaimer_style))
                            elements.append(Spacer(1, 3))
                    
                    # Build PDF
                    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                          rightMargin=cm, leftMargin=cm, 
                                          topMargin=5*cm, bottomMargin=3*cm)
                    doc.build(elements, onFirstPage=header_footer_with_logos, 
                             onLaterPages=header_footer_with_logos)
                    
                    buffer.seek(0)
                    return buffer
                
                with st.spinner("Generating Financial Goal Report..."):
                    try:
                        pdf = generate_financial_goal_pdf()
                        st.success("Financial Goal Report generated successfully!")
                        st.download_button(
                            label="✅ Download Financial Goal Report PDF",
                            data=pdf,
                            file_name=f"Financial_Goal_Report_{client_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 2. Investment Sheet Generator ---
def show_investment_sheet():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    show_header()
    show_back_button("back_investment")
    
    st.markdown("""
    <div class="goal-section">
        <h2>Investment Sheet Generator</h2>
        <p>Create comprehensive investment recommendations and portfolio allocations</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Client Details", "💼 Portfolio Configuration", "📄 Generate PDF"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            client_name = st.text_input("Client Name", placeholder="Enter client full name")
            report_date = st.text_input("Report Date", value=datetime.now().strftime("%d-%m-%Y"))
            financial_goal = st.text_input("Financial Goal", placeholder="e.g., Wealth Creation, Retirement Planning")
            
        with col2:
            investment_horizon = st.selectbox("Investment Horizon", ["Short Term (< 3 years)", "Medium Term (3-7 years)", "Long Term (> 7 years)"])
            risk_profile = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])
            
            default_return = ""
            if risk_profile == "Aggressive":
                default_return = "12-15%"
            elif risk_profile == "Moderate":
                default_return = "10-12%"
            elif risk_profile == "Conservative":
                default_return = "8-10%"
                
            return_expectation = st.text_input("Expected Returns", value=default_return)

        st.markdown("**Investment Amount**")
        col1, col2 = st.columns(2)
        
        with col1:
            investment_amount = st.text_input("Lumpsum Investment (Rs.)", placeholder="0")
        with col2:
            sip_amount = st.text_input("Monthly SIP Amount (Rs.)", placeholder="0")
        
        include_strategy_note = st.checkbox("Include Investment Strategy Description")
        if include_strategy_note:
            strategy_note = st.text_area("Strategy Description", 
                                        value="""Out of Rs. 35.00 lacs,
• An amount of Rs 7.00 Lacs will be invested directly into Equity Funds.
• Balance amount of Rs. 28.00 lacs will be invested into Debt funds, we will start STP (Systematic Transfer Plan) of
 Rs. 3.50 lacs every fortnight or according to the market opportunities from Debt Funds to Equity Funds till August 2025.
This is an important point to note.""", 
                                        height=100)
    
    with tab2:
        st.markdown("**Select Tables to Include**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            include_lumpsum = st.checkbox("Lumpsum Allocation")
            include_sip = st.checkbox("SIP Allocation")
            include_fund_perf = st.checkbox("Fund Performance Analysis")
            
        with col2:
            include_initial_stp = st.checkbox("Initial Investment (STP Clients)")
            include_final_stp = st.checkbox("Final Portfolio (Post STP)")

        lumpsum_alloc = None
        if include_lumpsum:
            with st.expander("Configure Lumpsum Allocation", expanded=True):
                default_lumpsum = [{"Category": "Equity", "SubCategory": "Mid Cap", "Scheme Name": "HDFC Mid Cap Fund", "Allocation (%)": 50.00, "Amount": 100000.00}]
                df = pd.DataFrame(default_lumpsum)
                lumpsum_alloc = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="lumpsum")

        sip_alloc = None
        if include_sip:
            with st.expander("Configure SIP Allocation", expanded=True):
                default_sip = [{"Category": "Equity", "SubCategory": "Small Cap", "Scheme Name": "SBI Small Cap Fund", "Allocation (%)": 50.00, "Amount": 5000.00}]
                df = pd.DataFrame(default_sip)
                sip_alloc = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="sip")

        fund_perf = None
        if include_fund_perf:
            with st.expander("Configure Fund Performance", expanded=True):
                fund_perf_data = [{"Scheme Name": "HDFC Mid Cap Fund", "PE": 25.50, "SD": 15.00, "SR": 1.20, "Beta": 0.90, "Alpha": 1.50, "1Y": 12.30, "3Y": 15.60, "5Y": 17.80, "10Y": 19.20}]
                fund_perf = st.data_editor(pd.DataFrame(fund_perf_data), num_rows="dynamic", use_container_width=True, key="fund_perf")

        initial_alloc = None
        if include_initial_stp:
            with st.expander("Configure Initial Investment (STP)", expanded=True):
                df = pd.DataFrame([{"Category": "", "SubCategory": "", "Scheme Name": "", "Allocation (%)": 0.0, "Amount": 0.0}])
                initial_alloc = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="initial_stp")

        final_alloc = None
        if include_final_stp:
            with st.expander("Configure Final Portfolio (Post STP)", expanded=True):
                df = pd.DataFrame([{"Category": "", "SubCategory": "", "Scheme Name": "", "Allocation (%)": 0.0, "Amount": 0.0}])
                final_alloc = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="final_stp")

        st.markdown("**Fund Factsheets**")
        factsheet_links = st.text_area("Factsheet Links", 
                                       placeholder="Format: Fund Name - Description | https://link.com\nOne link per line",
                                       height=80)

    with tab3:
        st.markdown("**PDF Generation**")
        
        if not client_name or not client_name.strip():
            st.warning("Please enter client name in the Client Details tab to generate PDF.")
        else:
            st.success(f"Ready to generate PDF for: **{client_name}**")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📄 Download Investment Sheet PDF", type="primary", use_container_width=True):
                    if not client_name.strip() or not report_date.strip():
                        st.error("Please enter both Client Name and Report Date.")
                    else:
                        with st.spinner("Generating Investment Sheet..."):
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
                                        elements.append(Spacer(1, 3))

                                doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=cm, leftMargin=cm, topMargin=5*cm, bottomMargin=3*cm)
                                doc.build(elements, onFirstPage=header_footer_with_logos, onLaterPages=header_footer_with_logos)
                                
                                buffer.seek(0)
                                return buffer

                            pdf = generate_investment_pdf()
                            st.success("Investment Sheet PDF generated successfully!")
                            st.download_button(
                                label="Download Investment Sheet PDF",
                                data=pdf,
                                file_name=f"Investment_Sheet_{client_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf"
                            )
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. Minutes of Meeting Generator ---
def show_minutes_of_meeting():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    show_header()
    show_back_button("back_mom")
    
    st.markdown("""
    <div class="goal-section">
        <h2>Minutes of Meeting</h2>
        <p>Create detailed meeting minutes with client information and investment details</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Meeting Title
    meeting_title = st.text_input("Meeting Title", value="Portfolio Review of")
    
    # Meeting Details
    st.markdown('<div class="info-card"><h3>📅 Meeting Information</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        meeting_organizer = st.text_input("Meeting Organizer", value="Mr. Puneet Kohli")
        meeting_date_time = st.text_input("Meeting Date & Time")
        
    with col2:
        meeting_location = st.text_input("Meeting Location")
        minutes_drafted_date = st.text_input("Minutes Drafted Date")
    
    # Investment Profile
    st.markdown('<div class="info-card"><h3>💼 Investment Profile</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        investment_horizon = st.selectbox("Investment Horizon", ["Short Term", "Medium Term", "Long Term"])
    with col2:
        risk_profile = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])
    with col3:
        return_expectation = st.text_input("Return Expectation", value="8% - 10% CAGR")
    with col4:
        awareness_level = st.selectbox("Awareness level", ["LOW", "MEDIUM", "HIGH"])
    
    # Brief Description/Agenda
    st.markdown('<div class="info-card"><h3>📋 Brief Description/Agenda</h3></div>', unsafe_allow_html=True)
    
    agenda_items = st.text_area("Meeting Agenda", 
                               value="- Review of Asset Allocation\n- Fund Review", 
                               height=100)
    
    # Asset Allocation Review
    st.markdown('<div class="calculation-card"><h3>🔍 Review of Asset Allocation</h3></div>', unsafe_allow_html=True)
    
    investor_name = st.text_input("Investor Name")
    
    # Asset Allocation Table
    st.markdown("**Current Asset Allocation**")
    asset_allocation_data = {
        'Category': ['Equity', 'Debt', 'Total'],
        'Percentage': [0.00, 0.00, 100],
        'Amount (Rs.)': [0.00, 0.00, 0.00]
    }
    
    asset_df = pd.DataFrame(asset_allocation_data)
    edited_allocation = st.data_editor(
        asset_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Percentage": st.column_config.NumberColumn("Percentage (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.2f"),
            "Amount (Rs.)": st.column_config.NumberColumn("Amount (Rs.)", min_value=0, step=1000, format="%.2f")
        }
    )
    
    # Further Action
    st.markdown('<div class="info-card"><h3>⚡ Further Action:</h3><p>Detail of Investment is as mention below in chart:</p></div>', unsafe_allow_html=True)
    
    # Investment Details Table
    investment_data = {
        'Sr. No.': [1, 2, 3, 4],
        'Scheme Type': ['EQUITY', 'DEBT', 'HYBRID', 'ARBITRAGE'],
        'Scheme Name': ['', '', '', ''],
        'Allocation (%)': [0.00, 0.00, 0.00, 0.00],
        'Amount (Rs.)': [0.00, 0.00, 0.00, 0.00]
    }
    
    investment_df = pd.DataFrame(investment_data)
    edited_investment = st.data_editor(
        investment_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Sr. No.": st.column_config.NumberColumn("Sr. No.", disabled=True),
            "Scheme Type": st.column_config.TextColumn("Scheme Type", disabled=True),
            "Scheme Name": st.column_config.TextColumn("Scheme Name"),
            "Allocation (%)": st.column_config.NumberColumn("Allocation (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.2f"),
            "Amount (Rs.)": st.column_config.NumberColumn("Amount (Rs.)", min_value=0, step=1000, format="%.2f")
        }
    )
    
    # Add Total row
    total_allocation = edited_investment['Allocation (%)'].sum()
    total_amount = edited_investment['Amount (Rs.)'].sum()
    
    st.markdown(f"**Total: {total_allocation:.2f}% | Rs.{format_indian_number(total_amount)}**")
    
    # Additional Notes
    st.markdown('<div class="info-card"><h3>📝 Additional Notes</h3></div>', unsafe_allow_html=True)
    
    additional_notes = st.text_area("Additional Discussion Points", height=100)
    
    # Generate PDF Button
    st.markdown('<div class="calculate-button">', unsafe_allow_html=True)
    if st.button("📄 Generate Minutes of Meeting PDF"):
        if investor_name:
            with st.spinner("Generating Minutes of Meeting..."):
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
                        [Paragraph("<b>Meeting Title</b>", info_table_style), Paragraph(f"<b>Portfolio Review of {investor_name}</b>", info_table_style)],
                        [Paragraph("<b>Meeting Organizer</b>", info_table_style), Paragraph(f"<b>{meeting_organizer}</b>", info_table_style)],
                        [Paragraph("<b>Meeting Date & Time</b>", info_table_style), Paragraph(f"<b>{meeting_date_time}</b>", info_table_style)],
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
                    
                    profile_text = f"<b>Investment Horizon:</b> {investment_horizon} &nbsp;&nbsp;&nbsp;&nbsp; <b>Risk Profile:</b> {risk_profile}<br/><br/><b>Return Expectation:</b> {return_expectation} &nbsp;&nbsp;&nbsp;&nbsp; <b>Awareness level:</b> {awareness_level}"
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
                        [Paragraph(f"<b>{investor_name}</b>", info_table_style), Paragraph(f"<b>{edited_allocation.at[0, 'Percentage']:.2f}%</b>", info_table_style), Paragraph(f"<b>{edited_allocation.at[1, 'Percentage']:.2f}%</b>", info_table_style), Paragraph("<b>100%</b>", info_table_style)]
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
                    
                    if not edited_investment.empty and not edited_investment.dropna(how='all').empty:
                        total_amount = edited_investment['Amount (Rs.)'].sum()
                        
                        investment_table_data = []
                        investment_table_data.append([
                            Paragraph("<b>Sr. No.</b>", info_table_style),
                            Paragraph("<b>Scheme Type</b>", info_table_style),
                            Paragraph("<b>Scheme Name</b>", info_table_style),
                            Paragraph("<b>Allocation (%)</b>", info_table_style),
                            Paragraph("<b>Amount (Rs.)</b>", info_table_style)
                        ])
                        
                        for index, row in edited_investment.iterrows():
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
                    
                    if additional_notes.strip():
                        elements.append(Paragraph("<b>Additional Notes:</b>", section_heading_style))
                        elements.append(Paragraph(additional_notes.replace('\n', '<br/>'), normal_style))
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
                        name='DisclaimerText', 
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
                
                pdf = generate_mom_pdf()
                st.success("Minutes of Meeting PDF generated successfully!")
                st.download_button(
                    label="Download Minutes of Meeting PDF",
                    data=pdf,
                    file_name=f"MOM_{investor_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
        else:
            st.error("Please enter Investor Name")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. Meeting Checklist Generator ---
def show_meeting_checklist():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    show_header()
    show_back_button("back_checklist")
    
    st.markdown("""
    <div class="goal-section">
        <h2>Meeting Checklist Generator</h2>
        <p>Customizable pre-meeting checklists to ensure comprehensive client discussions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Default checklist items
    default_checklist_items = [
        "Non NJ Portfolio Review",
        "Change in Financial Goals- Time & Amount",
        "Requirement of Funds in next 1,3,5 Years",
        "Any additional goals",
        "Performance against goals (tracker)",
        "Review of Asset Allocation- Current vs Proposed vs Original",
        "Review of Category Allocation- Current vs Proposed vs Original",
        "Changes Proposed",
        "Reason for change",
        "SIP Review",
        "Investment Plan",
        "Additional Family Account Opening",
        "Reference",
        "Insurance Review - Term/ Health / General",
        "Will Writing / Estate Planning",
        "Testimonial/ Wallet share",
        "Risk profile",
        "Money belief",
        "Collection of docs",
        "Anniversary",
        "Need an iPad",
        "Taking gifts along",
        "Carry all necessary forms",
        "Taking valuation report, SIP, Portfolio review report of existing portfolio",
        "Brochures & file ready"
    ]
    
    tab1, tab2, tab3 = st.tabs(["📋 Meeting Info", "✅ Checklist Items", "📄 Generate PDF"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            client_name_checklist = st.text_input("Client Name", placeholder="Enter client name")
            meeting_date_checklist = st.text_input("Meeting Date", placeholder="DD-MM-YYYY")
            
        with col2:
            meeting_time_checklist = st.text_input("Meeting Time", placeholder="HH:MM AM/PM")
            meeting_location_checklist = st.text_input("Meeting Location", placeholder="Enter location")
    
    with tab2:
        # Initialize session state
        if 'selected_checklist_items' not in st.session_state:
            st.session_state.selected_checklist_items = []
        
        st.markdown("**Select Checklist Items**")
        
        # Quick select buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Select All", use_container_width=True):
                st.session_state.selected_checklist_items = default_checklist_items.copy()
                st.rerun()
        
        with col2:
            if st.button("Clear All", use_container_width=True):
                st.session_state.selected_checklist_items = []
                st.rerun()
        
        with col3:
            if st.button("Select Top 10", use_container_width=True):
                st.session_state.selected_checklist_items = default_checklist_items[:10]
                st.rerun()
        
        st.markdown("---")
        
        # Display checkboxes for each item
        for i, item in enumerate(default_checklist_items):
            is_selected = item in st.session_state.selected_checklist_items
            
            if st.checkbox(item, value=is_selected, key=f"checkbox_{i}"):
                if item not in st.session_state.selected_checklist_items:
                    st.session_state.selected_checklist_items.append(item)
            else:
                if item in st.session_state.selected_checklist_items:
                    st.session_state.selected_checklist_items.remove(item)
        
        # Custom checklist items
        st.markdown("**Add Custom Items**")
        custom_item = st.text_input("Add custom checklist item", placeholder="Enter custom item")
        if st.button("Add Custom Item") and custom_item:
            if custom_item not in st.session_state.selected_checklist_items:
                st.session_state.selected_checklist_items.append(custom_item)
                st.success(f"Added: {custom_item}")
                st.rerun()
        
        # Show selected items count
        st.info(f"Selected {len(st.session_state.selected_checklist_items)} items")
    
    with tab3:
        st.markdown("**PDF Generation**")
        
        if not client_name_checklist or not client_name_checklist.strip():
            st.warning("Please enter client name in the Meeting Info tab to generate PDF.")
        elif not st.session_state.selected_checklist_items:
            st.warning("Please select at least one checklist item.")
        else:
            st.success(f"Ready to generate checklist for: **{client_name_checklist}**")
            st.info(f"Checklist contains **{len(st.session_state.selected_checklist_items)}** items")
            
            # Preview selected items
            with st.expander("Preview Selected Items"):
                for idx, item in enumerate(st.session_state.selected_checklist_items, 1):
                    st.write(f"{idx}. {item}")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📄 Download Meeting Checklist PDF", type="primary", use_container_width=True):
                    with st.spinner("Generating Meeting Checklist..."):
                        def generate_meeting_checklist_pdf():
                            buffer = BytesIO()
                            styles = getSampleStyleSheet()
                            
                            # Enhanced professional styles
                            title_style = ParagraphStyle(
                                name='Title', 
                                fontSize=20, 
                                leading=24, 
                                alignment=1, 
                                spaceAfter=25, 
                                fontName='Helvetica-Bold',
                                textColor=colors.black
                            )
                            
                            client_style = ParagraphStyle(
                                name='Client', 
                                parent=styles['Normal'], 
                                fontSize=12, 
                                leading=16, 
                                spaceAfter=10, 
                                fontName='Helvetica',
                                textColor=colors.black
                            )
                            
                            heading_style = ParagraphStyle(
                                name='Heading', 
                                fontSize=16, 
                                leading=20, 
                                spaceAfter=15, 
                                spaceBefore=20,
                                fontName='Helvetica-Bold',
                                textColor=colors.black
                            )
                            
                            checklist_style = ParagraphStyle(
                                name='Checklist', 
                                parent=styles['Normal'], 
                                fontSize=12, 
                                leading=18,  # Increased line spacing
                                leftIndent=15, 
                                spaceAfter=12,  # More space between items
                                fontName='Helvetica',
                                textColor=colors.black
                            )
                            
                            elements = []
                            
                            # Header with more space
                            elements.append(Paragraph("PRE-MEETING CHECKLIST", title_style))
                            elements.append(Spacer(1, 30))
                            
                            # Meeting details with better formatting
                            elements.append(Paragraph("Meeting Information", heading_style))
                            elements.append(Paragraph(f"<b>Client Name:</b> {client_name_checklist or '_' * 30}", client_style))
                            elements.append(Paragraph(f"<b>Meeting Date:</b> {meeting_date_checklist or '_' * 20}", client_style))
                            elements.append(Paragraph(f"<b>Meeting Time:</b> {meeting_time_checklist or '_' * 20}", client_style))
                            elements.append(Paragraph(f"<b>Location:</b> {meeting_location_checklist or '_' * 30}", client_style))
                            elements.append(Spacer(1, 25))
                            
                            # Checklist items with better spacing
                            elements.append(Paragraph("Checklist Items", heading_style))
                            elements.append(Spacer(1, 15))
                            
                            for item in st.session_state.selected_checklist_items:
                                # REMOVED numbers, just checkbox and item
                                checkbox_text = f"• {item}"
                                elements.append(Paragraph(checkbox_text, checklist_style))
                            
                            # Add page break before Additional Notes
                            elements.append(PageBreak())
                            
                            # Additional Notes section (FIXED VERSION)
                            elements.append(Spacer(1, 30))  # Space from top
                            elements.append(Paragraph("Additional Notes:", heading_style))
                            elements.append(Spacer(1, 20))
                            
                            # Create proper note lines (FIXED)
                            note_style = ParagraphStyle(
                                name='Notes', 
                                parent=styles['Normal'], 
                                fontSize=12, 
                                leading=20,  # Reduced line height
                                fontName='Helvetica',
                                textColor=colors.black
                            )
                            
                            # FIXED: Create continuous lines that fit on one page
                            for _ in range(8):
                                elements.append(Paragraph("_" * 80, styles['Normal']))
                                elements.append(Spacer(1, 12))
                            
                            # Build PDF with increased margins for better spacing
                            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                                   rightMargin=2.5*cm,   # Increased margins
                                                   leftMargin=2.5*cm, 
                                                   topMargin=6*cm,       # More space from header
                                                   bottomMargin=4*cm)    # More space from footer
                            doc.build(elements, onFirstPage=header_footer_with_logos, onLaterPages=header_footer_with_logos)
                            
                            buffer.seek(0)
                            return buffer
                        
                        pdf = generate_meeting_checklist_pdf()
                        st.success("Meeting Checklist PDF generated successfully!")
                        st.download_button(
                            label="Download Meeting Checklist PDF",
                            data=pdf,
                            file_name=f"Meeting_Checklist_{client_name_checklist.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf"
                        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. Multi-Asset Class Decision Analyzer ---
# --- 5. Multi-Asset Class Decision Analyzer ---
def show_asset_decision_analyzer():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    show_header()
    show_back_button("back_decision_analyzer")
    
    st.markdown("""
    <div class="goal-section">
        <h2>Multi-Asset Class Decision Analyzer</h2>
        <p>Real-time comparison across major asset classes to make informed investment decisions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for this module
    if 'asset_analysis_results' not in st.session_state:
        st.session_state.asset_analysis_results = {}
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Select Assets", "📊 Portfolio Input", "⚙️ Parameters", "📈 Analysis"])
    
    with tab1:
        st.markdown('### Select Asset Classes to Compare')
        st.markdown('<div class="info-card"><p>Choose the asset classes you want to compare for your investment decision</p></div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            include_mutual_funds = st.checkbox("📊 Mutual Funds", value=True, help="Equity, Debt, Hybrid mutual funds")
        with col2:
            include_real_estate = st.checkbox("🏠 Real Estate", help="Property investments, REITs")
        with col3:
            include_gold = st.checkbox("🥇 Gold", help="Physical gold, Gold ETFs, Digital gold")
        with col4:
            include_fd = st.checkbox("🏦 Fixed Deposits", help="Bank FDs, Corporate FDs with accrual tax")
    
    with tab2:
        st.markdown('### Current Portfolio Details')
        
        # Mutual Funds Section
        if include_mutual_funds:
            with st.expander("📊 Mutual Fund Portfolio", expanded=True):
                st.markdown("**Current Mutual Fund Holdings**")
                
                # Initialize MF data in session state
                if 'mf_schemes' not in st.session_state:
                    st.session_state.mf_schemes = pd.DataFrame({
                        'Scheme Name': [''],
                        'Category': ['Equity Large Cap'],
                        'Invested Amount (Rs.)': [0],
                        'Current Value (Rs.)': [0],
                        'Investment Date': [datetime.now().date()],
                        'Monthly SIP (Rs.)': [0]
                    })
                
                # Editable MF schemes table
                edited_mf = st.data_editor(
                    st.session_state.mf_schemes,
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config={
                        "Category": st.column_config.SelectboxColumn(
                            "Category",
                            options=["Equity Large Cap", "Equity Mid Cap", "Equity Small Cap", 
                                   "Debt Fund", "Hybrid Fund", "ELSS"],
                            required=True
                        ),
                        "Invested Amount (Rs.)": st.column_config.NumberColumn(
                            "Invested Amount (Rs.)", min_value=0, step=1000, format="%d"
                        ),
                        "Current Value (Rs.)": st.column_config.NumberColumn(
                            "Current Value (Rs.)", min_value=0, step=1000, format="%d"
                        ),
                        "Investment Date": st.column_config.DateColumn("Investment Date"),
                        "Monthly SIP (Rs.)": st.column_config.NumberColumn(
                            "Monthly SIP (Rs.)", min_value=0, step=500, format="%d"
                        )
                    },
                    hide_index=True
                )
                st.session_state.mf_schemes = edited_mf
        
        # Real Estate Section
        if include_real_estate:
            with st.expander("🏠 Real Estate Portfolio", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    property_purchase_value = st.number_input("Property Purchase Value (Rs.)", min_value=0, value=0, key="prop_purchase")
                    property_current_value = st.number_input("Current Market Value (Rs.)", min_value=0, value=0, key="prop_current")
                    property_purchase_date = st.date_input("Purchase Date", key="prop_date")
                with col2:
                    rental_income_monthly = st.number_input("Monthly Rental Income (Rs.)", min_value=0, value=0, key="rental_income")
                    property_type = st.selectbox("Property Type", ["Residential", "Commercial", "REIT"], key="prop_type")
                    maintenance_cost_annual = st.number_input("Annual Maintenance Cost (Rs.)", min_value=0, value=0, key="maintenance")
        
        # Gold Section
        if include_gold:
            with st.expander("🥇 Gold Investment", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    gold_investment_type = st.selectbox("Gold Investment Type", 
                                                      ["Physical Gold", "Gold ETF", "Digital Gold"], key="gold_type")
                    gold_purchase_price = st.number_input("Purchase Price per gram (Rs.)", min_value=0.0, value=0.0, key="gold_purchase_price")
                    gold_quantity = st.number_input("Quantity (grams)", min_value=0.0, value=0.0, key="gold_qty")
                with col2:
                    gold_current_price = st.number_input("Current Gold Price per gram (Rs.)", min_value=0.0, value=6500.0, key="gold_current_price")
                    gold_purchase_date = st.date_input("Purchase Date", key="gold_date")
                    storage_cost_annual = st.number_input("Annual Storage/Management Cost (Rs.)", min_value=0, value=0, key="gold_storage")
        
        # Fixed Deposits Section
        if include_fd:
            with st.expander("🏦 Fixed Deposit Options", expanded=False):
                st.info("💡 **Accrual Tax Impact**: Unlike mutual funds where tax is paid only on redemption, FD interest is taxed every year, reducing the effective compounding benefit.")
                
                col1, col2 = st.columns(2)
                with col1:
                    fd_amount = st.number_input("Amount to Invest in FD (Rs.)", min_value=0, value=0, key="fd_amount")
                    fd_rate = st.number_input("FD Interest Rate (% per annum)", min_value=0.0, max_value=15.0, value=7.5, step=0.25, key="fd_rate",
                                            help="Interest rate per annum. Note: FD interest is subject to annual accrual tax, which means tax is deducted yearly on interest earned, reducing effective compounded returns.")
                with col2:
                    fd_tenure = st.number_input("FD Tenure (Years)", min_value=1, max_value=10, value=3, key="fd_tenure")
                    fd_type = st.selectbox("FD Type", ["Regular FD", "Tax Saving FD", "Senior Citizen FD"], key="fd_type")
    
    with tab3:
        st.markdown('### Analysis Parameters')
        st.markdown('<div class="info-card"><p>Set your investment preferences and tax details for accurate comparison</p></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            investment_horizon = st.selectbox("Investment Horizon", 
                                            ["1 Year", "3 Years", "5 Years", "10 Years"], 
                                            index=2, key="horizon")
            current_age = st.number_input("Your Current Age", min_value=18, max_value=80, value=35, key="client_age")
        
        with col2:
            tax_bracket = st.selectbox("Tax Bracket", 
                                     ["5%", "20%", "30%"], 
                                     index=2, key="tax_bracket")
            inflation_rate = st.number_input("Expected Inflation Rate (%)", min_value=0.0, max_value=15.0, value=6.0, step=0.5, key="inflation")
        
        with col3:
            risk_tolerance = st.selectbox("Risk Tolerance", 
                                        ["Conservative", "Moderate", "Aggressive"], 
                                        index=1, key="risk_tolerance")
            liquidity_need = st.selectbox("Liquidity Requirement", 
                                        ["High", "Medium", "Low"], 
                                        index=1, key="liquidity")
    
    with tab4:
        st.markdown('### Investment Decision Analysis')
        
        # Check if at least one asset class is selected
        selected_assets = []
        if include_mutual_funds:
            selected_assets.append("Mutual Funds")
        if include_real_estate:
            selected_assets.append("Real Estate")
        if include_gold:
            selected_assets.append("Gold")
        if include_fd:
            selected_assets.append("Fixed Deposits")
        
        if not selected_assets:
            st.warning("Please select at least one asset class to compare.")
        else:
            st.info(f"Selected for comparison: {', '.join(selected_assets)}")
            
            st.markdown('<div class="calculate-button">', unsafe_allow_html=True)
            if st.button("🔄 Analyze Investment Options", use_container_width=True):
                with st.spinner("⚡ Analyzing your investment options..."):
                    
                    # Perform calculations
                    analysis_results = perform_comprehensive_asset_analysis(
                        include_mutual_funds, include_real_estate, include_gold, include_fd,
                        investment_horizon, tax_bracket, inflation_rate
                    )
                    
                    # Store results in session state
                    st.session_state.asset_analysis_results = analysis_results
                    
                    st.success("✅ Analysis completed successfully!")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display results if analysis is done
            if st.session_state.asset_analysis_results:
                display_comprehensive_analysis_results(st.session_state.asset_analysis_results, selected_assets)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Helper functions for asset analysis calculations
def perform_comprehensive_asset_analysis(include_mf, include_re, include_gold, include_fd, horizon, tax_bracket, inflation):
    results = {}
    horizon_years = int(horizon.split()[0])
    tax_rate = float(tax_bracket.strip('%')) / 100
    
    # Mutual Funds Analysis
    if include_mf and not st.session_state.mf_schemes.empty:
        mf_results = analyze_mutual_funds_comprehensive(st.session_state.mf_schemes, horizon_years, tax_rate)
        if mf_results:
            results['Mutual Funds'] = mf_results
    
    # Real Estate Analysis
    if include_re and st.session_state.get('prop_purchase', 0) > 0:
        re_results = analyze_real_estate_comprehensive(horizon_years, tax_rate, inflation)
        if re_results:
            results['Real Estate'] = re_results
    
    # Gold Analysis
    if include_gold and st.session_state.get('gold_qty', 0) > 0:
        gold_results = analyze_gold_comprehensive(horizon_years, tax_rate, inflation)
        if gold_results:
            results['Gold'] = gold_results
    
    # Fixed Deposits Analysis with Accrual Tax
    if include_fd and st.session_state.get('fd_amount', 0) > 0:
        fd_results = analyze_fd_with_accrual_tax(horizon_years, tax_rate)
        if fd_results:
            results['Fixed Deposits'] = fd_results
    
    return results

def analyze_mutual_funds_comprehensive(mf_data, years, tax_rate):
    # Filter out empty rows
    mf_data = mf_data[
        (mf_data['Invested Amount (Rs.)'] > 0) | 
        (mf_data['Current Value (Rs.)'] > 0)
    ]
    
    if mf_data.empty:
        return None
    
    total_invested = mf_data['Invested Amount (Rs.)'].sum()
    total_current = mf_data['Current Value (Rs.)'].sum()
    
    if total_invested == 0:
        return None
    
    current_gains = total_current - total_invested
    
    # Calculate tax implications based on holding period and category
    total_tax_impact = 0
    total_exit_load = 0
    
    for _, scheme in mf_data.iterrows():
        if scheme['Investment Date'] and pd.notna(scheme['Investment Date']):
            holding_days = (datetime.now().date() - scheme['Investment Date']).days
            gains = scheme['Current Value (Rs.)'] - scheme['Invested Amount (Rs.)']
            
            # Tax calculation based on category and holding period
            if scheme['Category'] in ['Equity Large Cap', 'Equity Mid Cap', 'Equity Small Cap', 'ELSS']:
                if holding_days > 365:  # LTCG
                    tax_on_gains = max(0, (gains - 100000) * 0.10) if gains > 100000 else 0
                else:  # STCG
                    tax_on_gains = gains * 0.15 if gains > 0 else 0
            else:  # Debt funds
                if holding_days > 1095:  # LTCG with indexation
                    tax_on_gains = gains * 0.20 if gains > 0 else 0
                else:  # STCG
                    tax_on_gains = gains * tax_rate if gains > 0 else 0
            
            total_tax_impact += tax_on_gains
            
            # Exit load (typically 1% if < 1 year)
            if holding_days < 365:
                total_exit_load += scheme['Current Value (Rs.)'] * 0.01
    
    net_proceeds = total_current - total_tax_impact - total_exit_load
    
    # Future projection based on asset mix
    equity_schemes = len(mf_data[mf_data['Category'].str.contains('Equity|ELSS', na=False)])
    debt_schemes = len(mf_data[mf_data['Category'].str.contains('Debt', na=False)])
    hybrid_schemes = len(mf_data[mf_data['Category'].str.contains('Hybrid', na=False)])
    
    total_schemes = len(mf_data)
    equity_ratio = equity_schemes / total_schemes
    debt_ratio = debt_schemes / total_schemes
    hybrid_ratio = hybrid_schemes / total_schemes
    
    expected_return = (equity_ratio * 12) + (debt_ratio * 7) + (hybrid_ratio * 9)
    
    future_value = total_current * ((1 + expected_return/100) ** years)
    
    return {
        'current_value': total_current,
        'invested_amount': total_invested,
        'current_gains': current_gains,
        'tax_impact': total_tax_impact,
        'exit_load': total_exit_load,
        'net_proceeds': net_proceeds,
        'future_value': future_value,
        'expected_return': expected_return,
        'liquidity': 'High',
        'risk_level': 'Medium to High' if equity_ratio > 0.5 else 'Low to Medium'
    }

def analyze_real_estate_comprehensive(years, tax_rate, inflation):
    purchase_value = st.session_state.get('prop_purchase', 0)
    current_value = st.session_state.get('prop_current', 0)
    rental_income = st.session_state.get('rental_income', 0) * 12
    maintenance_cost = st.session_state.get('maintenance', 0)
    
    if purchase_value == 0 or current_value == 0:
        return None
    
    current_gains = current_value - purchase_value
    holding_days = (datetime.now().date() - st.session_state.get('prop_date', datetime.now().date())).days
    
    # Tax calculation for real estate
    if holding_days > 730:  # LTCG (2 years for real estate)
        indexed_cost = purchase_value * (1 + inflation/100) ** (holding_days/365)
        taxable_gains = max(0, current_value - indexed_cost)
        tax_impact = taxable_gains * 0.20
    else:  # STCG
        tax_impact = current_gains * tax_rate if current_gains > 0 else 0
    
    net_proceeds = current_value - tax_impact
    
    # Future projection (real estate appreciation + rental yield)
    future_capital_value = current_value * ((1 + 8/100) ** years)
    future_rental_income = rental_income * years * (1 + inflation/100) ** (years/2)
    total_future_value = future_capital_value + future_rental_income - (maintenance_cost * years)
    
    return {
        'current_value': current_value,
        'invested_amount': purchase_value,
        'current_gains': current_gains,
        'tax_impact': tax_impact,
        'exit_load': 0,
        'net_proceeds': net_proceeds,
        'future_value': total_future_value,
        'expected_return': 8.0,
        'liquidity': 'Low',
        'risk_level': 'Medium'
    }

def analyze_gold_comprehensive(years, tax_rate, inflation):
    purchase_price = st.session_state.get('gold_purchase_price', 0)
    quantity = st.session_state.get('gold_qty', 0)
    current_price = st.session_state.get('gold_current_price', 0)
    storage_cost = st.session_state.get('gold_storage', 0)
    
    if purchase_price == 0 or quantity == 0 or current_price == 0:
        return None
    
    purchase_value = purchase_price * quantity
    current_value = current_price * quantity
    current_gains = current_value - purchase_value
    holding_days = (datetime.now().date() - st.session_state.get('gold_date', datetime.now().date())).days
    
    # Tax calculation for gold
    if holding_days > 1095:  # LTCG (3 years for gold)
        tax_impact = current_gains * 0.20 if current_gains > 0 else 0
    else:  # STCG
        tax_impact = current_gains * tax_rate if current_gains > 0 else 0
    
    net_proceeds = current_value - tax_impact
    
    # Future projection (gold typically beats inflation by 2-3%)
    future_value = current_value * ((1 + (inflation + 2)/100) ** years) - (storage_cost * years)
    
    return {
        'current_value': current_value,
        'invested_amount': purchase_value,
        'current_gains': current_gains,
        'tax_impact': tax_impact,
        'exit_load': 0,
        'net_proceeds': net_proceeds,
        'future_value': future_value,
        'expected_return': inflation + 2,
        'liquidity': 'Medium',
        'risk_level': 'Low to Medium'
    }

def analyze_fd_with_accrual_tax(years, tax_rate):
    """Analyze FD with proper accrual tax implementation"""
    principal = st.session_state.get('fd_amount', 0)
    annual_rate = st.session_state.get('fd_rate', 7.5)
    tenure = st.session_state.get('fd_tenure', 3)
    
    if principal == 0:
        return None
    
    # Calculate FD maturity with accrual tax (annual taxation of interest)
    amount = principal
    total_tax_paid = 0
    
    # Apply accrual tax year by year
    for year in range(min(years, tenure)):
        interest_earned = amount * annual_rate / 100
        tax_on_interest = interest_earned * tax_rate
        net_interest = interest_earned - tax_on_interest
        amount += net_interest
        total_tax_paid += tax_on_interest
    
    # If investment horizon is longer than FD tenure, reinvest at maturity
    if years > tenure:
        remaining_years = years - tenure
        for year in range(remaining_years):
            interest_earned = amount * annual_rate / 100
            tax_on_interest = interest_earned * tax_rate
            net_interest = interest_earned - tax_on_interest
            amount += net_interest
            total_tax_paid += tax_on_interest
    
    net_proceeds = amount
    effective_annual_return = ((amount / principal) ** (1/years) - 1) * 100
    
    return {
        'current_value': principal,
        'invested_amount': principal,
        'current_gains': 0,
        'tax_impact': total_tax_paid,
        'exit_load': 0,
        'net_proceeds': net_proceeds,
        'future_value': net_proceeds,
        'expected_return': effective_annual_return,
        'liquidity': 'Medium',
        'risk_level': 'Very Low'
    }

def display_comprehensive_analysis_results(results, selected_assets):
    st.markdown("## 📊 Investment Analysis Results")
    
    # Create comparison table
    comparison_data = []
    for asset_class, data in results.items():
        if data:
            comparison_data.append({
                'Asset Class': asset_class,
                'Current Value': f"Rs.{format_indian_number(data['current_value'])}",
                'Current Gains/Loss': f"Rs.{format_indian_number(data['current_gains'])}",
                'Tax Impact': f"Rs.{format_indian_number(data['tax_impact'])}",
                'Net Proceeds Today': f"Rs.{format_indian_number(data['net_proceeds'])}",
                'Future Value': f"Rs.{format_indian_number(data['future_value'])}",
                'Expected Return': f"{data['expected_return']:.1f}%",
                'Liquidity': data['liquidity'],
                'Risk Level': data['risk_level']
            })
    
    if comparison_data:
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Create visualizations
        st.markdown("### 📈 Visual Comparison")
        
        # Future value comparison chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Chart 1: Current vs Future Value
        asset_names = [data['Asset Class'] for data in comparison_data]
        current_values = [float(data['Current Value'].replace('Rs.', '').replace(',', '')) for data in comparison_data]
        future_values = [float(data['Future Value'].replace('Rs.', '').replace(',', '')) for data in comparison_data]
        
        x = range(len(asset_names))
        width = 0.35
        
        ax1.bar([i - width/2 for i in x], current_values, width, label='Current Value', color='#4facfe', alpha=0.7)
        ax1.bar([i + width/2 for i in x], future_values, width, label='Future Value', color='#00f2fe', alpha=0.7)
        
        ax1.set_xlabel('Asset Classes')
        ax1.set_ylabel('Value (Rs.)')
        ax1.set_title('Current vs Future Value Comparison')
        ax1.set_xticks(x)
        ax1.set_xticklabels(asset_names, rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Chart 2: Expected Returns
        returns = [float(data['Expected Return'].replace('%', '')) for data in comparison_data]
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4'][:len(asset_names)]
        
        ax2.bar(asset_names, returns, color=colors, alpha=0.7)
        ax2.set_xlabel('Asset Classes')
        ax2.set_ylabel('Expected Return (%)')
        ax2.set_title('Expected Annual Returns')
        ax2.set_xticklabels(asset_names, rotation=45)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        
        # Investment Recommendations
        st.markdown("### 💡 Investment Recommendations")
        
        best_return = max(comparison_data, key=lambda x: float(x['Expected Return'].replace('%', '')))
        
        risk_mapping = {'Very Low': 1, 'Low': 2, 'Low to Medium': 2.5, 'Medium': 3, 'Medium to High': 4, 'High': 5}
        lowest_risk = min(comparison_data, key=lambda x: risk_mapping.get(x['Risk Level'], 3))
        
        liquidity_mapping = {'Low': 1, 'Medium': 2, 'High': 3}
        highest_liquidity = max(comparison_data, key=lambda x: liquidity_mapping.get(x['Liquidity'], 2))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Highest Return Potential</div>
                <div class="metric-value">{best_return['Asset Class']}</div>
                <div class="metric-label">{best_return['Expected Return']} Expected Return</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Lowest Risk Option</div>
                <div class="metric-value">{lowest_risk['Asset Class']}</div>
                <div class="metric-label">{lowest_risk['Risk Level']} Risk</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Highest Liquidity</div>
                <div class="metric-value">{highest_liquidity['Asset Class']}</div>
                <div class="metric-label">{highest_liquidity['Liquidity']} Liquidity</div>
            </div>
            """, unsafe_allow_html=True)
        
        # PDF Generation
        st.markdown('<div class="calculate-button">', unsafe_allow_html=True)
        if st.button("📄 Generate Asset Comparison Report"):
            generate_comprehensive_asset_pdf(results, comparison_data, selected_assets)
        st.markdown('</div>', unsafe_allow_html=True)

def generate_comprehensive_asset_pdf(results, comparison_data, selected_assets):
    """Generate comprehensive PDF report for asset comparison with proper formatting"""
    buffer = BytesIO()
    styles = getSampleStyleSheet()
    
    # Define styles
    heading_style = ParagraphStyle(
        name='ReportHeading', 
        fontSize=20, 
        leading=24, 
        alignment=TA_CENTER,
        spaceAfter=20, 
        fontName='Helvetica-Bold',
        textColor=colors.black
    )
    
    subheading_style = ParagraphStyle(
        name='SubHeading',
        fontSize=14,
        leading=18,
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold',
        textColor=colors.black
    )
    
    normal_style = ParagraphStyle(
        name='Normal', 
        parent=styles['Normal'], 
        fontSize=10, 
        leading=14,
        fontName=UNICODE_FONT
    )
    
    # Header style for table with word wrapping
    header_cell_style = ParagraphStyle(
        name='HeaderCell',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        alignment=1,  # Center alignment
        fontName='Helvetica-Bold',
        wordWrap='CJK'
    )
    
    # Body cell style
    body_cell_style = ParagraphStyle(
        name='BodyCell',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        fontName=UNICODE_FONT
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph("Multi-Asset Class Investment Analysis Report", heading_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", subheading_style))
    elements.append(Paragraph(f"This report analyzes {len(selected_assets)} asset classes: {', '.join(selected_assets)}.", normal_style))
    elements.append(Spacer(1, 15))
    
    # Asset Comparison Table with FIXED column widths and wrapped headers
    elements.append(Paragraph("Asset Class Comparison", subheading_style))
    
    # Create table with wrapped headers
    table_data = []
    
    # Header row with wrapped text
    header_row = [
        Paragraph("Asset Class", header_cell_style),
        Paragraph("Current Value", header_cell_style),
        Paragraph("Net Proceeds Today", header_cell_style),
        Paragraph("Future Value", header_cell_style),
        Paragraph("Expected Return", header_cell_style),
        Paragraph("Risk Level", header_cell_style)
    ]
    table_data.append(header_row)
    
    # Data rows
    for data in comparison_data:
        table_data.append([
            Paragraph(data['Asset Class'], body_cell_style),
            Paragraph(data['Current Value'], body_cell_style),
            Paragraph(data['Net Proceeds Today'], body_cell_style),
            Paragraph(data['Future Value'], body_cell_style),
            Paragraph(data['Expected Return'], body_cell_style),
            Paragraph(data['Risk Level'], body_cell_style)
        ])
    
    # FIXED column widths to prevent spill-over
    comparison_table = Table(table_data, colWidths=[2.8*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.2*cm, 2.5*cm])
    comparison_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#E6F3F8')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # Right align values
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    
    elements.append(comparison_table)
    elements.append(Spacer(1, 20))
    
    # Investment Recommendations
    elements.append(Paragraph("Investment Recommendations", subheading_style))
    
    best_return = max(comparison_data, key=lambda x: float(x['Expected Return'].replace('%', '')))
    elements.append(Paragraph(f"• <b>Highest Return Potential:</b> {best_return['Asset Class']} with {best_return['Expected Return']} expected annual return", normal_style))
    
    risk_mapping = {'Very Low': 1, 'Low': 2, 'Low to Medium': 2.5, 'Medium': 3, 'Medium to High': 4, 'High': 5}
    lowest_risk = min(comparison_data, key=lambda x: risk_mapping.get(x['Risk Level'], 3))
    elements.append(Paragraph(f"• <b>Lowest Risk Option:</b> {lowest_risk['Asset Class']} with {lowest_risk['Risk Level']} risk profile", normal_style))
    
    liquidity_mapping = {'Low': 1, 'Medium': 2, 'High': 3}
    highest_liquidity = max(comparison_data, key=lambda x: liquidity_mapping.get(x['Liquidity'], 2))
    elements.append(Paragraph(f"• <b>Highest Liquidity:</b> {highest_liquidity['Asset Class']} offers {highest_liquidity['Liquidity']} liquidity", normal_style))
    
    elements.append(Spacer(1, 20))
    
    # Important Tax Considerations
    elements.append(Paragraph("Important Tax Considerations", subheading_style))
    elements.append(Paragraph("• <b>Accrual Tax on Fixed Deposits:</b> FD interest is taxed annually, reducing effective compounding returns", normal_style))
    elements.append(Paragraph("• Mutual fund taxes are deferred until redemption (STCG/LTCG applicable)", normal_style))
    elements.append(Paragraph("• Real estate enjoys indexation benefits for LTCG after 2 years", normal_style))
    elements.append(Paragraph("• Gold has LTCG benefits after 3 years of holding", normal_style))

    # Add Charts Section
    elements.append(PageBreak())
    elements.append(Paragraph("Visual Analysis", subheading_style))
    
    # Create matplotlib charts - STACKED VERTICALLY
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))  # Changed from (1, 2) to (2, 1)

    # Extract data for charts
    asset_names = [data['Asset Class'] for data in comparison_data]
    current_values = [float(data['Current Value'].replace('Rs.', '').replace(',', '')) for data in comparison_data]
    future_values = [float(data['Future Value'].replace('Rs.', '').replace(',', '')) for data in comparison_data]
    returns = [float(data['Expected Return'].replace('%', '')) for data in comparison_data]

    # Chart 1: Current vs Future Value (TOP)
    x = range(len(asset_names))
    width = 0.35

    ax1.bar([i - width/2 for i in x], current_values, width, label='Current Value', 
            color='#4facfe', alpha=0.8)
    ax1.bar([i + width/2 for i in x], future_values, width, label='Future Value', 
            color='#00f2fe', alpha=0.8)

    ax1.set_xlabel('Asset Classes')
    ax1.set_ylabel('Value (Rs.)')
    ax1.set_title('Current vs Future Value Comparison', fontweight='bold', fontsize=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels(asset_names, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')

    # Chart 2: Expected Returns (BOTTOM)
    colors_list = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4'][:len(asset_names)]

    bars = ax2.bar(asset_names, returns, color=colors_list, alpha=0.8)
    ax2.set_xlabel('Asset Classes')
    ax2.set_ylabel('Expected Return (%)')
    ax2.set_title('Expected Annual Returns', fontweight='bold', fontsize=12)
    ax2.set_xticklabels(asset_names, rotation=45, ha='right')
    ax2.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for bar, value in zip(bars, returns):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()  # Important for vertical stacking

    # Save chart to buffer and add to PDF
    chart_buffer = BytesIO()
    plt.savefig(chart_buffer, format='png', bbox_inches='tight', dpi=300)
    plt.close(fig)
    chart_buffer.seek(0)

    # Insert chart into PDF with adjusted dimensions
    chart_image = Image(chart_buffer, width=14*cm, height=12*cm)  # Adjusted height for vertical layout
    elements.append(chart_image)
    elements.append(Spacer(1, 20))

    
    
    # Page break before disclaimer
    elements.append(PageBreak())
    
    # Disclaimer
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("DISCLAIMER", ParagraphStyle(
        name='DisclaimerHeading', 
        fontSize=16, 
        leading=24, 
        alignment=TA_CENTER,
        spaceAfter=25, 
        fontName='Helvetica-Bold'
    )))
    
    disclaimer_style = ParagraphStyle(
        name='DisclaimerStyle', 
        parent=styles['Normal'], 
        fontSize=9, 
        leading=11,
        fontName=UNICODE_FONT
    )
    
    # Add special note about FD accrual tax
    elements.append(Paragraph("*Important: Fixed Deposit (FD) interest is subject to annual accrual tax which reduces compounding returns. This means tax is deducted yearly on interest earned, significantly impacting the final maturity amount compared to investments where tax is deferred until redemption.", disclaimer_style))
    elements.append(Spacer(1, 10))
    
    disclaimer_paragraphs = [p.strip() for p in DISCLAIMER_TEXT.split('.') if p.strip()]
    for paragraph in disclaimer_paragraphs:
        if paragraph:
            elements.append(Paragraph(paragraph + ".", disclaimer_style))
            elements.append(Spacer(1, 3))
    
    # Build PDF with consistent header and footer
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                          rightMargin=cm, leftMargin=cm, 
                          topMargin=5*cm, bottomMargin=3*cm)
    doc.build(elements, onFirstPage=header_footer_with_logos, 
             onLaterPages=header_footer_with_logos)
    
    buffer.seek(0)
    
    st.success("Asset Comparison Report generated successfully!")
    st.download_button(
        label="✅ Download Asset Comparison Report PDF",
        data=buffer,
        file_name=f"Asset_Comparison_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )



# --- Main App Logic ---
def main():
    if st.session_state.app_mode is None:
        show_main_screen()
    elif st.session_state.app_mode == "investment":
        show_investment_sheet()
    elif st.session_state.app_mode == "goal_planner":
        show_financial_goal_planner()
    elif st.session_state.app_mode == "mom":
        show_minutes_of_meeting()
    elif st.session_state.app_mode == "checklist":
        show_meeting_checklist()
    elif st.session_state.app_mode == "decision_analyzer":  # ADD THIS LINE
        show_asset_decision_analyzer()

if __name__ == "__main__":
    main()
