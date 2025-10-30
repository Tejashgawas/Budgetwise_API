from app.extensions import db
from datetime import datetime


class User(db.Model):
    """User model for storing user information."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship("Transaction", back_populates="user", cascade="all, delete")



    def __repr__(self):
        return f'<User {self.username}>'
    