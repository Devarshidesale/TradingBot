import logging
from dataclasses import dataclass

from client import send_order, APIError, NetworkError


log = logging.getLogger(__name__)


# Clean result container

@dataclass
class OrderResult:
    success:      bool
    order_id:     int    = 0
    status:       str    = ""
    executed_qty: str    = ""
    price:        str    = ""
    error:        str    = ""


# Market order

def place_market_order(symbol: str, side: str, quantity: float) -> OrderResult:
    params = {
        "symbol":   symbol,
        "side":     side.upper(),
        "type":     "MARKET",
        "quantity": quantity,
    }

    try:
        resp = send_order(params)
        print(resp)
    except APIError as exc:
        log.error("Market order failed — APIError %s: %s", exc.code, exc.msg)
        return OrderResult(success=False, error=str(exc))
    except NetworkError as exc:
        log.error("Market order failed — NetworkError: %s", exc.reason)
        return OrderResult(success=False, error=str(exc))

    return OrderResult(
        success=True,
        order_id=resp["orderId"],
        status=resp["status"],
        executed_qty=resp.get("executedQty", "0"),
        price=resp.get("avgPrice", "0"),
    )


# Limit order

def place_limit_order(symbol: str, side: str, quantity: float, price: float) -> OrderResult:
    params = {
        "symbol":      symbol,
        "side":        side.upper(),
        "type":        "LIMIT",
        "timeInForce": "GTC",
        "quantity":    quantity,
        "price":       price,
    }

    try:
        resp = send_order(params)
        print(resp)
    except APIError as exc:
        log.error("Limit order failed — APIError %s: %s", exc.code, exc.msg)
        return OrderResult(success=False, error=str(exc))
    except NetworkError as exc:
        log.error("Limit order failed — NetworkError: %s", exc.reason)
        return OrderResult(success=False, error=str(exc))

    finalObject = OrderResult(
        success=True,
        order_id=resp["orderId"],
        status=resp["status"], 
        executed_qty=resp.get("executedQty", "0"),
        price=resp.get("price", "0"),
    )
    return finalObject

print(place_limit_order("BTCUSDT", "BUY", 0.01, 50000))
