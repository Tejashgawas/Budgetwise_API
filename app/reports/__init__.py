from flask import Blueprint

reports_blueprint = Blueprint("reports", __name__)

from . import routes  
