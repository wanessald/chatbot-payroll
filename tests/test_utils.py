from decimal import Decimal
from app.utils import format_currency

def test_format_currency_decimal():
    value = Decimal("1234.56")
    assert format_currency(value) == "R$ 1.234,56"

def test_format_currency_rounding():
    value = Decimal("1234.567")
    assert format_currency(value) == "R$ 1.234,57"
