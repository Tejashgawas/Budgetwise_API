from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from flask import current_app

from app.services.auth_services import AuthService
from app.schemas.auth_schema import (
    RegisterResponse,
    LoginResponse,
    LogoutResponse,
    UserDetailResponse,
)
from app.utils.protected import auth_required
from app.schemas.auth_schema import RegisterSchema, LoginSchema  # your request schemas


auth_bp = Blueprint("auth", __name__)


# -----------------------------
# REGISTER
# -----------------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        validated_data = RegisterSchema(**data)

        response, status = AuthService.register_user(
            username=validated_data.username,
            email=validated_data.email,
            password=validated_data.password,
        )
        
        return jsonify(RegisterResponse(**response).model_dump()), status

    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Unexpected error: {str(e)}"}), 500


# -----------------------------
# LOGIN
# -----------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        validated_data = LoginSchema(**data)

        response, status = AuthService.login_user(
            email=validated_data.email,
            password=validated_data.password,
        )
       
        return jsonify(LoginResponse(**response).model_dump()), status

    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400
    except ValueError as e:
        return jsonify({"message": str(e)}), 401
    except Exception as e:
        
        return jsonify({"message": f"Unexpected error: {str(e)}"}), 500


# -----------------------------
# GET CURRENT USER
# -----------------------------
@auth_bp.route("/me", methods=["GET"])
@auth_required
def get_current_user():
    try:
        user_id = request.user_id
        current_app.logger.debug(f"[USER] Fetching details for user_id: {user_id}")
        response, status = AuthService.get_user(user_id)
        
        # Convert response to Pydantic model and back to ensure validation
        validated_response = UserDetailResponse(**response)
        current_app.logger.debug(f"[USER] Successfully retrieved user details: {validated_response}")
        
        return jsonify(validated_response.model_dump()), status

    except ValidationError as e:
       
        return jsonify({"message": "Data validation error", "details": str(e)}), 422
    except ValueError as e:
        
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"[USER] Unexpected error: {str(e)}")
        return jsonify({"message": f"Unexpected error: {str(e)}"}), 500


# -----------------------------
# LOGOUT
# -----------------------------
@auth_bp.route("/logout", methods=["POST"])
def logout():
    try:
        response, status = AuthService.logout()
        return jsonify(LogoutResponse(**response).model_dump()), status
    except Exception as e:
        return jsonify({"message": f"Unexpected error: {str(e)}"}), 500
