import csv
from decimal import Decimal
from datetime import datetime
from typing import List
from pydantic import ValidationError
from app.models import Category, Transaction
from app.extensions import db
from app.schemas.transaction_schemas import TransactionCreateSchema
from app.services.transaction_service import create_transaction

def import_transactions_via_route(csv_path: str,user_id:int):
    """
    Reads a CSV file, validates and converts each row to TransactionCreateSchema,
    calls create_transaction() for each row, and returns a summary.

    CSV Format:
        category_name,type,amount,description,date
    Example:
        Food,expense,250.50,Lunch at cafe,2025-10-25
    """
    success_count = 0
    fail_count = 0
    results = []

    with open(csv_path, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for idx, row in enumerate(reader, start=1):
            try:
                # Map CSV row to Pydantic schema
                tx_schema = TransactionCreateSchema(
                    category_name=row.get("category_name", "").strip() or None,
                    type=row["type"].strip(),
                    amount=Decimal(row["amount"]),
                    description=row.get("description", "").strip() or None,
                    date=datetime.strptime(row["date"], "%Y-%m-%d").date() if row.get("date") else None
                )

                # Call the existing service to add transaction
                create_transaction(user_id, tx_schema)
                success_count += 1
                results.append({"row": idx, "status": "success"})

            except (ValidationError, ValueError) as e:
                fail_count += 1
                results.append({"row": idx, "status": "failed", "error": str(e), "data": row})

            except Exception as e:
                fail_count += 1
                results.append({"row": idx, "status": "error", "error": str(e), "data": row})

    return {
        "message": "✅ CSV import completed",
        "success_count": success_count,
        "failed_count": fail_count,
        "details": results
    }
