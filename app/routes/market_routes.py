from flask import Blueprint, jsonify
from app.utils.market_format import market_service


market_bp = Blueprint("market", __name__, url_prefix="/market")


# --------------------------------------
# Global Stock Price (Yahoo Finance)
# --------------------------------------
@market_bp.get("/stock/<name>")
def get_stock_price(name):
    data = market_service.global_stock(name)


    if data is None:
        return jsonify({"error": "Stock not found"}), 404

    return jsonify(data)


# --------------------------------------
# Nifty 50
# --------------------------------------
@market_bp.get("/nifty50")
def nifty50():
    data = market_service.nifty()

    if data is None:
        return jsonify({"error": "Nifty50 data unavailable"}), 404

    return jsonify(data)


# --------------------------------------
# Sensex
# --------------------------------------
@market_bp.get("/sensex")
def sensex():
    data = market_service.sensex()

    if data is None:
        return jsonify({"error": "Sensex data unavailable"}), 404

    return jsonify(data)
