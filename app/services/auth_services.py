from app.extensions import db
from app.models.user import User
from app.utils.security import hash_password, verify_password,create_jwt_token

class AuthService:
    """Handles user registration and login."""

    @staticmethod
    def register_user(username:str,email:str,password:str):
        """Registers a new user."""
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            raise ValueError("Username or email already exists.")
        
        new_user = User(
            username=username,
            email=email,
            password_hash=hash_password(password)
        )
        db.session.add(new_user)
        db.session.commit()

        return {
            "message": "User registered successfully.",
            "user" : {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email
            }
        },201

    @staticmethod
    def login_user(email:str,password:str):
        """Authenticates a user and returns a JWT token."""
        user = User.query.filter_by(email=email).first()

        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid username or password.")
        
        token = create_jwt_token(user.id)
        
        return {
            "message": "Login successful.",
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        },200
    
    @staticmethod
    def get_user(user_id: int):
        """Fetch user details by ID (usually from decoded JWT)."""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found.")

        if user.created_at:
            formatted_date = user.created_at.strftime("%B %d, %Y at %I:%M %p")  # e.g., "October 29, 2025 at 10:23 AM"
        else:
            formatted_date = None

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": formatted_date
        }, 200


    @staticmethod
    def logout():
        """Handles user logout."""
        # In a stateless JWT authentication, logout can be handled on the client side
        
        return {
            "message": "Logout successful."
        },200