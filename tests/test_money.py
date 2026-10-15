from decimal import Decimal

import pytest

from susu.errors import ValidationError
from susu.money import parse_money


def test_parse_money_is_exact():
    assert parse_money("0.10") + parse_money("0.20") == Decimal("0.30")


def test_parse_money_rejects_three_decimals():
    with pytest.raises(ValidationError):
        parse_money("10.005")


@pytest.mark.parametrize("bad", ["abc", "", "NaN", "inf", 1.5])
def test_parse_money_rejects_garbage(bad):
    with pytest.raises(ValidationError):
        parse_money(bad)