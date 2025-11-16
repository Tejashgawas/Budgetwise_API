import os
import csv
from io import BytesIO, StringIO
from datetime import datetime, date
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak


# Register font
try:
    pdfmetrics.registerFont(TTFont("HelveticaNeue", "HelveticaNeue.ttf"))
    FONT_NAME = "HelveticaNeue"
except Exception:
    FONT_NAME = "Helvetica"


# =================================================================================
# 🔵 PDF GENERATION (Dynamic, keeps original design)
# =================================================================================
def generate_pdf_report(user_id, user_name, user_email, transactions,
                        start_date=None, end_date=None):
    """
    Generate PDF using old beautiful design but dynamic transaction data.
    """

    today = date.today()
    if not start_date:
        start_date = today.replace(day=1)
    if not end_date:
        end_date = today

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=40,
    )

    elements = []
    styles = getSampleStyleSheet()

    # -----------------------------------------------------------
    # Header Section
    # -----------------------------------------------------------
    header_table_data = []

    logo_path = os.path.join("app", "static", "logo.png")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.2 * inch, height=0.3 * inch)
    else:
        logo = Paragraph("<b>BudgetWise</b>", styles["Normal"])

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontName=FONT_NAME,
        fontSize=18,
        textColor=colors.HexColor("#2C3E50"),
        alignment=1,
    )
    title = Paragraph("", title_style)

    header_table_data.append([logo, title])
    header_table = Table(header_table_data, colWidths=[120, 400])
    header_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # -----------------------------------------------------------
    # User Info Section
    # -----------------------------------------------------------
    user_style = ParagraphStyle(
        "UserInfo",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=11,
        textColor=colors.HexColor("#2C3E50"),
    )

    user_info = [
        Paragraph(f"<b>USER NAME:</b> {user_name.upper()}", user_style),
        Paragraph(f"<b>USER ID:</b> {user_id}", user_style),
        Paragraph(f"<b>EMAIL:</b> {user_email}", user_style),
        Paragraph(f"<b>PERIOD:</b> {start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')}", user_style),
        Paragraph(f"<b>GENERATED ON:</b> {datetime.now().strftime('%d %B %Y, %I:%M %p')}", user_style),
    ]

    for item in user_info:
        elements.append(item)
    elements.append(Spacer(1, 25))

    # -----------------------------------------------------------
    # Transactions Table with Manual Pagination (15 per page)
    # -----------------------------------------------------------

    elements.append(Paragraph("<b>Transaction Details</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    table_header = [
        ["Date", "Transaction ID", "Type", "Category", "Amount", "Notes"]
    ]

    # -----------------------------------------------------------
    # Auto-calculate page capacity (rows per page)
    # -----------------------------------------------------------
    estimated_row_height = 18      # in points (approx based on your font/spacing)
    header_height = 40             # height of table header row
    usable_height = A4[1] - doc.topMargin - doc.bottomMargin - 200  # adjust based on header/userinfo

    rows_per_page = int((usable_height - header_height) / estimated_row_height)

    if rows_per_page < 10:
        rows_per_page = 10  # minimum safety


    # Split transactions into chunks based on rows_per_page
    # PAGE_SIZE = 15
    chunks = [transactions[i:i + rows_per_page] for i in range(0, len(transactions), rows_per_page)]

    for index, chunk in enumerate(chunks):
        table_rows = []

        # Build rows for this page
        for t in chunk:
            notes = Paragraph(t.description or "-", ParagraphStyle(
                "NotesWrap",
                parent=styles["Normal"],
                fontSize=9,
                leading=11,
                fontName=FONT_NAME,
            ))
            serial = index * rows_per_page + (chunk.index(t) + 1)  # Global sequential number
            hybrid_id = f"TX-{serial} (ID:{t.id})"
            table_rows.append([
                t.created_date.strftime("%Y-%m-%d") if t.created_date else "N/A",
                hybrid_id,
                t.type.title(),
                t.category.name if t.category else "N/A",
                f"${t.amount:.2f}",
                notes
            ])
        
        # Combine header + rows
        table_data = table_header + table_rows

        # --------------------------------------------
        # Dynamic column widths that WILL ALWAYS FIT
        # --------------------------------------------
        # Available page width
        available_width = A4[0] - doc.leftMargin - doc.rightMargin
        col_widths = [
            60,    # Date
            75,    # Txn ID
            70,    # Type
            90,    # Category
            55,    # Amount
            available_width - (60 + 45 + 70 + 90 + 55)  # Notes auto-fills remaining
        ]

        table = Table(table_data, repeatRows=1, hAlign="LEFT", colWidths=col_widths,splitByRow=True)

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498DB")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),

            ("ALIGN", (0, 1), (-2, -1), "LEFT"),
            ("ALIGN", (-2, 1), (-2, -1), "RIGHT"),  # Amount

            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
            ("FONTSIZE", (0, 0), (-1, -1), 9),

            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#ECF0F1")),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#BDC3C7")),
        ]))

        # Add table to PDF
        elements.append(table)
        elements.append(Spacer(1, 12))

        # Add page break UNLESS it's the last page
        if index < len(chunks) - 1:
            elements.append(PageBreak())



    # -----------------------------------------------------------
    # Summary Section (Dynamic)
    # -----------------------------------------------------------
    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expense = sum(t.amount for t in transactions if t.type == "expense")
    net_balance = total_income - total_expense

    elements.append(Paragraph("<b>Summary</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    summary_data = [
        ["Total Income", f"${total_income:.2f}"],
        ["Total Expenses", f"${total_expense:.2f}"],
        ["Net Balance", f"${net_balance:.2f}"],
    ]

    summary_table = Table(summary_data, hAlign="LEFT", colWidths=[180, 150])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8F9F9")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2C3E50")),
        ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#BDC3C7")),
    ]))
    elements.append(summary_table)

    # -----------------------------------------------------------
    # Footer Section
    # -----------------------------------------------------------
    def footer(canvas, doc):
        canvas.saveState()
        footer_text = "BudgetWise © 2025 — Personal Finance Tracker"
        canvas.setFont(FONT_NAME, 9)
        canvas.setFillColor(colors.HexColor("#7F8C8D"))
        canvas.drawCentredString(A4[0] / 2.0, 30, footer_text)
        canvas.restoreState()

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    pdf = buffer.getvalue()
    buffer.close()

    return pdf


# =================================================================================
# 🔵 CSV GENERATION (Dynamic)
# =================================================================================
def generate_csv_report(user_id, user_name, user_email, transactions):
    """
    CSV with original layout + dynamic data.
    """

    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)

    # Header row
    writer.writerow(["Date", "Transaction ID", "Transaction Type", "Category Type", "Amount", "Notes"])

    # Transaction rows
    for i,t in enumerate(transactions):
        hybrid_id = f"TX-{i+1} (ID:{t.id})"
        writer.writerow([
            t.created_date.strftime("%Y-%m-%d") if t.created_date else "N/A",
            hybrid_id,
            t.type.title(),
            t.category.name if t.category else "N/A",
            f"{t.amount:.2f}",
            t.description or "-"
        ])

    # Summary
    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expense = sum(t.amount for t in transactions if t.type == "expense")
    balance = total_income - total_expense

    writer.writerow([])
    writer.writerow(["Summary"])
    writer.writerow(["Total Income", f"{total_income:.2f}"])
    writer.writerow(["Total Expenses", f"{total_expense:.2f}"])
    writer.writerow(["Net Balance", f"{balance:.2f}"])

    return csv_buffer.getvalue()
