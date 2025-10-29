from functools import wraps
from flask import request,jsonify

from utils.security import decode_jwt_token
import jwt


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            return jsonify({"message": "Authorization header is missing"}), 401

        try:
            token = auth_header.split(" ")[1]
            user_id = decode_jwt_token(token)
            request.user_id = user_id
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"message": str(e)}), 401

        return f(*args, **kwargs)

    return decorated_function