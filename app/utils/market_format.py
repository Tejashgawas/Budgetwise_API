from app.services.market_service import (
    get_global_stock_price,
    get_nifty50_index,
    get_sensex_index
)


class MarketService:

    def format_output(self, symbol, name, price, open_price, high, low, source):
        percent_change = None
        if open_price and price:
            percent_change = round(((price - open_price) / open_price) * 100, 2)

        return {
            "symbol": symbol,
            "name": name,
            "price": price,
            "open": open_price,
            "high": high,
            "low": low,
            "percent_change": percent_change,
            "source": source
        }

    # ----------------------------
    # GLOBAL STOCKS
    # ----------------------------
    def global_stock(self, symbol: str):
        data = get_global_stock_price(symbol)

        if data is None:
            return None

        return self.format_output(
            symbol=symbol.upper(),
            name=f"{symbol.upper()} Stock",
            price=data["price"],
            open_price=data["open"],
            high=data["high"],
            low=data["low"],
            source="global"
        )

    # ----------------------------
    # NIFTY50
    # ----------------------------
    def nifty(self):
        data = get_nifty50_index()

        if data is None:
            return None

        return self.format_output(
            symbol="NIFTY50",
            name="NIFTY 50 Index",
            price=data["last"],
            open_price=data["open"],
            high=data["high"],
            low=data["low"],
            source="india-index"
        )

    # ----------------------------
    # SENSEX
    # ----------------------------
    def sensex(self):
        data = get_sensex_index()

        if data is None:
            return None

        return self.format_output(
            symbol="SENSEX",
            name="S&P BSE Sensex",
            price=data.get("last") or data.get("current") or data.get("price"),
            open_price=data.get("open") or data.get("day_open"),
            high=data.get("high") or data.get("day_high"),
            low=data.get("low") or data.get("day_low"),
            source="india-index"
        )


market_service = MarketService()
