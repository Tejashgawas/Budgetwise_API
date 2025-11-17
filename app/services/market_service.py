import yfinance as yf
from nsepython import nsefetch
import time
import requests

nifty_cache = {
    "data": None,
    "timestamp": 0,
    "open_price": None
}

sensex_cache = {
    "data": None,
    "timestamp": 0,
    "open_price": None
}

CACHE_TTL = 5 


# --------------------------------------
# GLOBAL STOCKS (Yahoo Finance)
# --------------------------------------
# def yahoo_search_symbol(query: str):
#     url = "https://query2.finance.yahoo.com/v1/finance/search"
#     params = {"q": query, "quotesCount": 1, "newsCount": 0}

#     try:
#         res = requests.get(url, params=params, timeout=5)
#         data = res.json()

#         quotes = data.get("quotes")
#         if not quotes:
#             return None

#         # best match
#         symbol = quotes[0].get("symbol")
#         print(symbol)
#         return symbol

#     except Exception:
#         return None
    
def get_global_stock_price(symbol: str):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1d")

    if hist.empty:
        return None

    return {
        "symbol": symbol.upper(),
        "price": float(hist["Close"].iloc[-1]),
        "open": float(hist["Open"].iloc[-1]),
        "high": float(hist["High"].iloc[-1]),
        "low": float(hist["Low"].iloc[-1])
    }



# --------------------------------------
# INDIAN INDEXES (NSE India)
# --------------------------------------
def get_nifty50_index():
    now = time.time()

    # If cache expired → fetch again
    if now - nifty_cache["timestamp"] > CACHE_TTL:

        url = "https://www.nseindia.com/api/allIndices"
        data = nsefetch(url)

        found = None
        for idx in data.get("data", []):
            if idx["index"] == "NIFTY 50":
                found = idx
                break

        if not found:
            return None   # Nifty not found

        # Cache data
        nifty_cache["data"] = found
        nifty_cache["timestamp"] = now

        # Store OPEN price only once
        if nifty_cache["open_price"] is None:
            nifty_cache["open_price"] = found.get("open")

    # --- Use cached data ---
    output = dict(nifty_cache["data"])  # copy
    output["open"] = nifty_cache["open_price"]
    return output

def get_sensex_index():
    now = time.time()

    # Cache expired → try to refresh
    if now - sensex_cache["timestamp"] > CACHE_TTL:

        try:
            ticker = yf.Ticker("^BSESN")
            hist = ticker.history(period="1d", timeout=10)

            # If Yahoo gives no data → use cached version instead of failing
            if hist.empty:
                if sensex_cache["data"]:
                    output = dict(sensex_cache["data"])
                    output["open"] = sensex_cache["open_price"]
                    return output
                return None  # no cache and no data

            # Build fresh data
            latest_data = {
                "index": "SENSEX",
                "price": float(hist["Close"].iloc[-1]),
                "open": float(hist["Open"].iloc[-1]),
                "high": float(hist["High"].iloc[-1]),
                "low": float(hist["Low"].iloc[-1])
            }

            # Cache the data
            sensex_cache["data"] = latest_data
            sensex_cache["timestamp"] = now

            # Preserve OPEN price
            if sensex_cache["open_price"] is None:
                sensex_cache["open_price"] = latest_data["open"]

        except Exception:
            # Fail-safe: return last known data
            if sensex_cache["data"]:
                output = dict(sensex_cache["data"])
                output["open"] = sensex_cache["open_price"]
                return output

            return None

    # Cached data is valid → return it
    output = dict(sensex_cache["data"])
    output["open"] = sensex_cache["open_price"]
    return output
