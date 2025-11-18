from flask import jsonify, send_file, request, Blueprint
from io import BytesIO
from datetime import datetime, date
from app.models.transaction import Transaction
from app.models.user import User

from app.services.export_services import generate_csv_report, generate_pdf_report
from app.utils.protected import auth_required
from datetime import datetime, date
from app.utils.export_exceptions import DateFormatError
from app.utils.export_exceptions import PDFGenerationError
from app.utils.export_exceptions import CSVGenerationError


export_bp = Blueprint("export", __name__)


@export_bp.route('/pdf', methods=['GET'])
@auth_required
def download_pdf():
    """Generate and download user-specific PDF report"""

    user_id = request.user_id
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    # optional date filters
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    type = request.args.get("type", "all")

    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            print(start_date)
        else:
            start_date = date.today().replace(day=1)

        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            print(end_date)
        else:
            end_date = date.today()

        if start_date > end_date:
            raise DateFormatError("start_date cannot be after end_date.")
        
        if type in ["income", "expense"]:
            transactions = (
            Transaction.query
            .filter(Transaction.user_id == user_id)
            .filter(Transaction.created_date >= start_date)
            .filter(Transaction.created_date <= end_date)
            .filter(Transaction.type == type)
            .all()
            )
        else:
            transactions = (
            Transaction.query
            .filter(Transaction.user_id == user_id)
            .filter(Transaction.created_date >= start_date)
            .filter(Transaction.created_date <= end_date)
            .all()
            )

    except ValueError:
        raise DateFormatError("Invalid date format. Expected YYYY-MM-DD.")

    if not transactions:
        return jsonify({"message": "No transactions found for this period."}), 404

    try:
        pdf_bytes = BytesIO(
            generate_pdf_report(
                user_id=user_id,
                user_name=user.username,
                user_email=user.email,
                transactions=transactions,
                start_date=start_date,
                end_date=end_date
            )
        )
    except Exception as e:
        raise PDFGenerationError(str(e))

    pdf_bytes.seek(0)

    return send_file(
        pdf_bytes,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='budgetwise_report.pdf'
    )


@export_bp.route('/csv', methods=['GET'])
@auth_required
def download_csv():
    """Generate CSV report with dynamic transaction data"""

    user_id = request.user_id
    user = User.query.get(user_id)
    type = request.args.get("type", "all")

    if not user:
        return jsonify({"message": "User not found"}), 404

    # optional date filters
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        else:
            start_date = date.today().replace(day=1)

        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        else:
            end_date = date.today()

        if start_date > end_date:
            raise DateFormatError("start_date cannot be after end_date.")
        
        if type in ["income", "expense"]:
            transactions = (
            Transaction.query
            .filter(Transaction.user_id == user_id)
            .filter(Transaction.created_date >= start_date)
            .filter(Transaction.created_date <= end_date)
            .filter(Transaction.type == type)
            .all()
            )
        else:
            transactions = (
            Transaction.query
            .filter(Transaction.user_id == user_id)
            .filter(Transaction.created_date >= start_date)
            .filter(Transaction.created_date <= end_date)
            .all()
            )

    except ValueError:
        raise DateFormatError("Invalid date format. Expected YYYY-MM-DD.")

    if not transactions:
        return jsonify({"message": "No transactions found for this period."}), 404

    try:
        csv_data = generate_csv_report(
            user_id=user_id,
            user_name=user.username,
            user_email=user.email,
            transactions=transactions
        )
    except Exception as e:
        raise CSVGenerationError(str(e))

    csv_bytes = BytesIO()
    csv_bytes.write(csv_data.encode("utf-8"))
    csv_bytes.seek(0)

    return send_file(
        csv_bytes,
        mimetype='text/csv',
        as_attachment=True,
        download_name='budgetwise_report.csv'
    )