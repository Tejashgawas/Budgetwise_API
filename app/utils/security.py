import bcrypt
import jwt
from datetime import datetime, timedelta
from flask import current_app


# --------------------------
# Password Hashing Utilities
# --------------------------


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hashed value."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

# --------------------------
# JWT Token Utilities
# --------------------------

def create_jwt_token(user_id:int,expires_in:int = 3600) -> str:
    """Create a JWT token with an expiration time."""
    payload = {
        "exp": datetime.utcnow() + timedelta(seconds=expires_in),
        "iat": datetime.utcnow(),
        "sub": user_id
    }

    secret_key = current_app.config.get("JWT_SECRET_KEY")
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

def decode_jwt_token(token: str) -> dict:
    """
    Decode and verify JWT token.
    Raises jwt exceptions if invalid or expired.
    """
    secret = current_app.config.get("SECRET_KEY")
    decoded = jwt.decode(token, secret, algorithms=["HS256"])
    return decoded.get("sub")