VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


def validate_symbol(symbol: str) -> str:
    if not symbol or not symbol.strip():
        raise ValueError("Symbol must not be empty.")
    return symbol.strip().upper()


def validate_side(side: str) -> str:
    cleaned = side.strip().upper()
    if cleaned not in VALID_SIDES:
        raise ValueError(f"Side must be BUY or SELL, got '{side}'.")
    return cleaned


def validate_order_type(order_type: str) -> str:
    cleaned = order_type.strip().upper()
    if cleaned not in VALID_ORDER_TYPES:
        raise ValueError(f"Order type must be MARKET or LIMIT, got '{order_type}'.")
    return cleaned


def validate_quantity(quantity) -> float:
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(f"Quantity must be a number, got '{quantity}'.")
    if qty <= 0:
        raise ValueError(f"Quantity must be positive, got {qty}.")
    return qty


def validate_price(price, order_type: str) -> float | None:
    if order_type == "MARKET":
        return None

    # LIMIT — price is required
    if price is None:
        raise ValueError("Price is required for LIMIT orders.")
    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValueError(f"Price must be a number, got '{price}'.")
    if p <= 0:
        raise ValueError(f"Price must be positive, got {p}.")
    return p


def validate_all(symbol: str, side: str, order_type: str, quantity, price=None) -> dict:
    clean_symbol     = validate_symbol(symbol)
    clean_side       = validate_side(side)
    clean_order_type = validate_order_type(order_type)
    clean_quantity   = validate_quantity(quantity)
    clean_price      = validate_price(price, clean_order_type)

    return {
        "symbol":     clean_symbol,
        "side":       clean_side,
        "order_type": clean_order_type,
        "quantity":   clean_quantity,
        "price":      clean_price,
    }
