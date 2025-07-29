def generate_pdf():
    buffer = BytesIO()
    styles = getSampleStyleSheet()

    link_text_style = ParagraphStyle(
        name='LinkText',
        parent=styles['Normal'],
        textColor=colors.blue,
        underline=1,
        fontSize=10
    )

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

    elements = [
        Spacer(1, 70),  # Push content below logo
        Paragraph("Investment Sheet", heading_style),
        Paragraph(f"<b>Client Name:</b> {client_name}", client_style),
        Paragraph(f"<b>Date:</b> {report_date}", client_style),
        Paragraph(f"<b>Financial Goal:</b> {financial_goal}", client_style),
        Paragraph(f"<b>Investment Horizon:</b> {investment_horizon}", client_style),
        Paragraph(f"<b>Risk Profile:</b> {risk_profile}", client_style),
        Paragraph(f"<b>Return Expectation:</b> {return_expectation}", client_style)
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
                note_paragraph_style = ParagraphStyle(
                    'note_paragraph_style',
                    parent=note_style,
                    leftIndent=0,
                    firstLineIndent=0,
                    spaceBefore=0,
                    leading=10,
                    fontSize=7
                )
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
        Paragraph(line.strip(), disclaimer_style)
        for line in disclaimer_text.strip().splitlines()
    ]
    elements.extend(disclaimer_elements)

    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=cm, leftMargin=cm, topMargin=cm, bottomMargin=cm)
    doc.build(elements, onFirstPage=header_footer_with_logos, onLaterPages=header_footer_with_logos)

    buffer.seek(0)
    return buffer
