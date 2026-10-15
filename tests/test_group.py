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

def test_week_cannot_close_when_someone_owes():
    group = make_group("Ama", "Kofi", "Esi")
    group.record_contribution("Ama", "50")
    group.record_contribution("Kofi", "50")
    group.record_contribution("Esi", "30")
    result = group.close_week()
    assert result.closed is False
    assert result.owing == {"Esi": Decimal("20.00")}
    assert group.payouts == []
    assert group.current_week == 1


def test_full_example_from_brief():
    group = make_group("Ama", "Kofi", "Esi")
    for name, amt in [("Ama", "50"), ("Kofi", "50"), ("Esi", "30")]:
        group.record_contribution(name, amt)
    assert not group.close_week().closed
    group.record_contribution("Esi", "20")
    result = group.close_week()
    assert result.closed
    assert result.payout.member == "Ama"
    assert result.payout.amount == Decimal("150.00")
    assert group.current_week == 2
    assert group.next_recipient() == "Kofi"


def test_payouts_follow_join_order_and_cycle_ends():
    group = make_group("Ama", "Kofi", amount="10.00")
    for _ in range(2):
        for name in group.members:
            group.record_contribution(name, "10")
        group.close_week()
    assert [p.member for p in group.payouts] == ["Ama", "Kofi"]
    assert group.is_complete
    with pytest.raises(StateError):
        group.close_week()


def test_money_is_exact_with_awkward_amounts():
    group = make_group("A", "B", "C", amount="33.33")
    for name in group.members:
        group.record_contribution(name, "33.33")
    assert group.close_week().payout.amount == Decimal("99.99")