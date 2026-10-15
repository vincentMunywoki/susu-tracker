from decimal import Decimal

import pytest

from susu.errors import (DuplicateMemberError, StateError, UnknownMemberError,
                         ValidationError)
from susu.group import SusuGroup


def make_group(*names, amount="50.00"):
    group = SusuGroup(amount)
    for name in names:
        group.add_member(name)
    return group


def test_group_requires_positive_weekly_amount():
    with pytest.raises(ValidationError):
        SusuGroup("0")


def test_duplicate_member_rejected_case_insensitive():
    group = make_group("Ama")
    with pytest.raises(DuplicateMemberError):
        group.add_member("  ama ")

def test_partial_payment_is_tracked():
    group = make_group("Ama", "Kofi")
    remaining = group.record_contribution("Ama", "30.00")
    assert remaining == Decimal("20.00")
    assert group.outstanding() == {"Ama": Decimal("20.00"), "Kofi": Decimal("50.00")}


def test_overpayment_rejected():
    group = make_group("Ama")
    group.record_contribution("Ama", "30")
    with pytest.raises(ValidationError):
        group.record_contribution("Ama", "20.01")


@pytest.mark.parametrize("bad", ["0", "-5", "0.00"])
def test_zero_or_negative_rejected(bad):
    group = make_group("Ama")
    with pytest.raises(ValidationError):
        group.record_contribution("Ama", bad)


def test_unknown_member_rejected():
    group = make_group("Ama")
    with pytest.raises(UnknownMemberError):
        group.record_contribution("Yaw", "10")


def test_cannot_add_member_after_contributions_start():
    group = make_group("Ama")
    group.record_contribution("Ama", "10")
    with pytest.raises(StateError):
        group.add_member("Kofi")