from dataclasses import dataclass
from decimal import Decimal

from .errors import (DuplicateMemberError, StateError, UnknownMemberError,
                     ValidationError)
from .money import fmt, parse_money


@dataclass(frozen=True)
class Payout:
    week: int
    member: str
    amount: Decimal


@dataclass(frozen=True)
class CloseResult:
    closed: bool
    payout: Payout | None
    owing: dict  # member -> Decimal still owed (empty when closed)


class SusuGroup:
    def __init__(self, weekly_amount):
        amount = parse_money(weekly_amount)
        if amount <= 0:
            raise ValidationError("Weekly contribution must be greater than zero.")
        self.weekly_amount = amount
        self._members: list[str] = []
        self._paid: dict[str, Decimal] = {}  # paid so far in the current week
        self.current_week = 1
        self.payouts: list[Payout] = []
        self._started = False  # becomes True on the first recorded contribution

    # ---- members ----
    @property
    def members(self) -> tuple:
        return tuple(self._members)

    @property
    def pot(self) -> Decimal:
        return self.weekly_amount * len(self._members)

    def _find(self, name: str) -> str:
        key = " ".join(str(name).split()).casefold()
        for member in self._members:
            if member.casefold() == key:
                return member
        raise UnknownMemberError(f"Unknown member '{name}'.")

    def add_member(self, name: str) -> str:
        clean = " ".join(str(name).split())
        if not clean:
            raise ValidationError("Member name cannot be empty.")
        if self._started:
            raise StateError(
                "Membership is locked once the first contribution is recorded.")
        if clean.casefold() in (m.casefold() for m in self._members):
            raise DuplicateMemberError(f"Member '{clean}' already exists.")
        self._members.append(clean)  # join order = payout order
        self._paid[clean] = Decimal("0.00")
        return clean
        # ---- contributions ----
    @property
    def is_complete(self) -> bool:
        return bool(self._members) and len(self.payouts) == len(self._members)

    def owed_by(self, name: str) -> Decimal:
        return self.weekly_amount - self._paid[self._find(name)]

    def record_contribution(self, name: str, amount, week: int | None = None) -> Decimal:
        """Record a (possibly partial) payment. Returns what the member still owes."""
        if self.is_complete:
            raise StateError("The cycle is complete; every member has been paid.")
        member = self._find(name)
        value = parse_money(amount)
        if value <= 0:
            raise ValidationError("Amount must be greater than zero.")
        if week is not None and week != self.current_week:
            raise ValidationError(
                f"Only the current week ({self.current_week}) accepts contributions.")
        owed = self.weekly_amount - self._paid[member]
        if value > owed:
            raise ValidationError(
                f"{member} only owes GHS {fmt(owed)} this week; cannot pay GHS {fmt(value)}.")
        self._paid[member] += value
        self._started = True
        return self.weekly_amount - self._paid[member]

    def outstanding(self) -> dict:
        return {m: self.weekly_amount - p
                for m, p in self._paid.items() if p < self.weekly_amount}

    def paid_in_full(self) -> list:
        return [m for m in self._members if self._paid[m] == self.weekly_amount]
    