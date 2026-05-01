import sys
import argparse

sys.path.insert(0, __import__("os").path.join(__import__("os").path.dirname(__file__), "bot"))

from client import APIError, NetworkError
from orders import place_market_order, place_limit_order
from logging_config import get_logger


log = get_logger()


# Argument parser

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Binance Futures Order CLI")

    parser.add_argument("--symbol",   type=str,   required=True,  help="Trading pair (e.g. BTCUSDT)")
    parser.add_argument("--side",     type=str,   required=True,  choices=["BUY", "SELL"], help="Order side")
    parser.add_argument("--type",     type=str,   required=True,  choices=["MARKET", "LIMIT"], dest="order_type", help="Order type")
    parser.add_argument("--quantity", type=float, required=True,  help="Order quantity")
    parser.add_argument("--price",    type=float, default=None,   help="Limit price (required for LIMIT orders)")

    return parser


# Main entry point

def main():
    parser = build_parser()
    args = parser.parse_args()

    symbol     = args.symbol.upper()
    side       = args.side.upper()
    order_type = args.order_type.upper()
    quantity   = args.quantity
    price      = args.price

    # 1. Validate (delegates to validators.py)
    try:
        from validators import validate_all
        validate_all(symbol=symbol, side=side, order_type=order_type, quantity=quantity, price=price)
    except ImportError:
        log.warning("validators module not ready — skipping validation")
    except ValueError as exc:
        print(f"[FAIL] Validation Error: {exc}")
        sys.exit(1)

    # 2. Print order summary
    if order_type == "LIMIT":
        print(f"Placing LIMIT {side} | {symbol} | qty={quantity} | price={price}")
    else:
        print(f"Placing MARKET {side} | {symbol} | qty={quantity}")

    log.info("Submitting %s %s order for %s qty=%s price=%s", order_type, side, symbol, quantity, price)

    # 3. Execute order
    try:
        if order_type == "MARKET":
            result = place_market_order(symbol, side, quantity)
        else:
            if price is None:
                print("[FAIL] Validation Error: --price is required for LIMIT orders")
                sys.exit(1)
            result = place_limit_order(symbol, side, quantity, price)

    except APIError as exc:
        log.error("APIError %s: %s", exc.code, exc.msg)
        print(f"[FAIL] API Error: code={exc.code} | msg={exc.msg}")
        sys.exit(1)

    except NetworkError as exc:
        log.error("NetworkError: %s", exc.reason)
        print("[FAIL] Network Error: Could not reach Binance. Check connection.")
        sys.exit(1)

    except Exception as exc:
        log.exception("Unexpected error")
        print(f"[FAIL] Unexpected error: {exc}")
        sys.exit(1)

    # 4. Print result
    if result.success:
        print("[OK] Order placed successfully")
        print(f"orderId={result.order_id} | status={result.status} | executedQty={result.executed_qty} | price={result.price}")
        log.info("Order success: id=%s status=%s", result.order_id, result.status)
    else:
        print(f"[FAIL] Order failed: {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
