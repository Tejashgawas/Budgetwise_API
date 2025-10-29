from functools import wraps
from flask import request, jsonify, current_app
from app.utils.security import decode_jwt_token
import jwt

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            current_app.logger.warning("[AUTH] Missing Authorization header.")
            return jsonify({"message": "Authorization header is missing"}), 401

        try:
            # Extract Bearer token
            parts = auth_header.split(" ")
            if len(parts) != 2 or parts[0].lower() != "bearer":
                
                return jsonify({"message": "Invalid Authorization header format"}), 401

            token = parts[1]
           

            # Decode and verify token
            current_app.logger.debug("[JWT] About to decode token")
            decoded_payload = decode_jwt_token(token)
            user_id = decoded_payload.get("sub")
            
            if not user_id:
                current_app.logger.warning("[AUTH] Token decoded but no 'sub' (user ID) found.")
                return jsonify({"message": "Not authenticated"}), 403
                
            # Convert string user_id back to integer
            request.user_id = int(user_id)
            
          

            request.user_id = user_id
            current_app.logger.debug(f"[AUTH] Authenticated user ID: {user_id}")

        except jwt.ExpiredSignatureError:
            current_app.logger.warning("[AUTH] Token has expired.")
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        except Exception as e:
            current_app.logger.error(f"[AUTH] Unexpected error: {e}")
            return jsonify({"message": str(e)}), 401

        # Proceed to the protected route
        return f(*args, **kwargs)

    return decorated_function
