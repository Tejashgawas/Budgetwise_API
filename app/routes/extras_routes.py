from flask import Blueprint, Response, jsonify, request
from app.services.extras import Extras
from app.utils.protected import auth_required

extras_bp = Blueprint('extras', __name__)

@extras_bp.route('/getdifference', methods=['GET'])
@auth_required
def get_extras():
    user_id = request.user_id

    result = Extras.calculateDifference(user_id)

    return jsonify(result)
