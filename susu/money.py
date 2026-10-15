from decimal import Decimal, InvalidOperation

from .errors import ValidationError

TWO_PLACES = Decimal("0.01")


def parse_money(value) -> Decimal:
    """Parse a GHS amount exactly. Never uses floats; rejects >2 decimal places."""
    if isinstance(value, float):
        raise ValidationError("Floats are not accepted for money; use a string like '50.00'.")
    try:
        amount = Decimal(str(value).strip())
    except InvalidOperation:
        raise ValidationError(f"'{value}' is not a valid amount.") from None
    if not amount.is_finite():
        raise ValidationError(f"'{value}' is not a valid amount.")
    if amount != amount.quantize(TWO_PLACES):
        raise ValidationError("Amounts can have at most 2 decimal places.")
    return amount.quantize(TWO_PLACES)


def fmt(amount: Decimal) -> str:
    return f"{amount:.2f}"