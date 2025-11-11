from flask import make_response
from app.reports.utils import generate_pdf_report, generate_csv_report
from . import reports_blueprint


@reports_blueprint.route("/generate-pdf", methods=["GET"])
def generate_pdf():
    pdf_data = generate_pdf_report(
        user_id=1,
        user_name="John Doe",
        user_email="johndoe@example.com"
    )
    response = make_response(pdf_data)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=BudgetWise_Report.pdf"
    return response


@reports_blueprint.route("/generate-csv", methods=["GET"])
def generate_csv():
    csv_data = generate_csv_report(
        user_id=1,
        user_name="John Doe",
        user_email="johndoe@example.com"
    )
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=BudgetWise_Report.csv"
    response.headers["Content-Type"] = "text/csv"
    return response
