from flask import jsonify, send_file, request, Blueprint
from io import BytesIO
from datetime import datetime, date
from app.models.transaction import Transaction
from app.models.user import User
from app.utils.export_utils import generate_pdf_report, generate_csv_report
from app.utils.protected import auth_required

export_bp = Blueprint("export", __name__)


@export_bp.route('/download/pdf', methods=['GET'])
@auth_required
def download_pdf():
    """Generate and download user-specific PDF report"""

    user_id = request.user_id
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    # optional date filters
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    else:
        start_date = date.today().replace(day=1)

    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    else:
        end_date = date.today()

    transactions = (
        Transaction.query
        .filter(Transaction.user_id == user_id)
        .filter(Transaction.created_date >= start_date)
        .filter(Transaction.created_date <= end_date)
        .all()
    )

    if not transactions:
        return jsonify({"message": "No transactions found for this period."}), 404

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

    pdf_bytes.seek(0)

    return send_file(
        pdf_bytes,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='budgetwise_report.pdf'
    )


@export_bp.route('/download/csv', methods=['GET'])
@auth_required
def download_csv():
    """Generate CSV report with dynamic transaction data"""

    user_id = request.user_id
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    transactions = Transaction.query.filter_by(user_id=user_id).all()

    if not transactions:
        return jsonify({"message": "No transactions found for this user."}), 404

    csv_data = generate_csv_report(
        user_id=user_id,
        user_name=user.username,
        user_email=user.email,
        transactions=transactions
    )

    csv_bytes = BytesIO()
    csv_bytes.write(csv_data.encode("utf-8"))
    csv_bytes.seek(0)

    return send_file(
        csv_bytes,
        mimetype='text/csv',
        as_attachment=True,
        download_name='budgetwise_report.csv'
    )
