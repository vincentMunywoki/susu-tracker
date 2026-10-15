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