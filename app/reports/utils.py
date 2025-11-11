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


# ✅ Register font
try:
    pdfmetrics.registerFont(TTFont("HelveticaNeue", "HelveticaNeue.ttf"))
    FONT_NAME = "HelveticaNeue"
except Exception:
    FONT_NAME = "Helvetica"


# ================================================================
# ✅ PDF GENERATION
# ================================================================
def generate_pdf_report(user_id=None, user_name="John Doe", user_email="john@example.com",
                        start_date=None, end_date=None):
    """Generate a clean, minimalist financial report PDF."""

    # 🗓️ Period calculation
    today = date.today()
    if not start_date:
        start_date = today.replace(day=1)
    if not end_date:
        end_date = today

    # 🧾 Create PDF buffer
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

    # --- Header Section ---
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
        alignment=1,  # center
    )
    # title = Paragraph("<br/><br/>BudgetWise — Financial Summary Report", title_style)
    title = Paragraph("", title_style)

    header_table_data.append([logo, title])
    header_table = Table(header_table_data, colWidths=[120, 400])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # --- User Info ---
    user_style = ParagraphStyle(
        "UserInfo",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=11,
        textColor=colors.HexColor("#2C3E50"),
    )

    user_info = [
        Paragraph(f"<b>USER NAME:</b> {user_name.upper()}", user_style),
        Paragraph(f"<b>USER ID:</b> {user_id or 'N/A'}", user_style),
        Paragraph(f"<b>EMAIL:</b> {user_email}", user_style),
        Paragraph(f"<b>PERIOD:</b> {start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')}", user_style),
        Paragraph(f"<b>GENERATED ON:</b> {datetime.now().strftime('%d %B %Y, %I:%M %p')}", user_style),
    ]

    for item in user_info:
        elements.append(item)
    elements.append(Spacer(1, 25))

    # --- Transactions Table ---
    elements.append(Paragraph("<b>Transaction Details</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    data = [
        ["Date", "Transaction ID", "Transaction Type", "Category Type", "Amount", "Notes"],
        ["2025-11-01", "TXN001", "Income", "Salary", "$1500", "-"],
        ["2025-11-02", "TXN002", "Expense", "Food", "$50", "Lunch"],
        ["2025-11-03", "TXN003", "Expense", "Transport", "$20", "Bus fare"],
    ]

    table = Table(data, repeatRows=1, hAlign="LEFT", colWidths=[75, 85, 90, 100, 65, 90])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498DB")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#ECF0F1")),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#BDC3C7")),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 25))

    # --- Summary Section ---
    elements.append(Paragraph("<b>Summary</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    summary_data = [
        ["Total Income", "$3,200"],
        ["Total Expenses", "$2,450"],
        ["Net Balance", "$750"],
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

    # --- Footer (Pinned Bottom) ---
    def footer(canvas, doc):
        canvas.saveState()
        footer_text = "BudgetWise © 2025 — Personal Finance Tracker"
        canvas.setFont(FONT_NAME, 9)
        canvas.setFillColor(colors.HexColor("#7F8C8D"))
        canvas.drawCentredString(A4[0] / 2.0, 30, footer_text)
        canvas.restoreState()

    # Build PDF
    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    pdf = buffer.getvalue()
    buffer.close()

    return pdf


# ================================================================
# ✅ CSV GENERATION
# ================================================================
def generate_csv_report(user_id=None, user_name="John Doe", user_email="john@example.com"):
    """Generate a simple CSV file with Transactions + Summary"""

    # --- Dummy Transactions ---
    transactions = [
        ["Date", "Transaction ID", "Transaction Type", "Category Type", "Amount", "Notes"],
        ["2025-11-01", "TXN001", "Income", "Salary", "1500", "-"],
        ["2025-11-02", "TXN002", "Expense", "Food", "50", "Lunch"],
        ["2025-11-03", "TXN003", "Expense", "Transport", "20", "Bus fare"],
    ]

    # --- Summary Section ---
    summary = [
        [],
        ["Summary"],
        ["Total Income", "3200"],
        ["Total Expenses", "2450"],
        ["Net Balance", "750"],
    ]

    # Write to memory
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerows(transactions)
    writer.writerows(summary)

    csv_data = csv_buffer.getvalue()
    csv_buffer.close()
    return csv_data
