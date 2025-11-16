
from app.extensions import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255))
    type = db.Column(db.String(50), nullable=False)  # e.g., 'income' or 'expense'
    
    created_date = db.Column(db.Date, default=datetime.utcnow) #reverted to old (removed .date)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.id} - {self.type}: {self.amount}>"