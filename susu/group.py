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
       
        # ---- closing a week ----
    def next_recipient(self) -> str | None:
        if self.is_complete:
            return None
        return self._members[len(self.payouts)]

    def close_week(self) -> CloseResult:
        if not self._members:
            raise StateError("Add at least one member before closing a week.")
        if self.is_complete:
            raise StateError("The cycle is complete; there are no more weeks.")
        owing = self.outstanding()
        if owing:
            return CloseResult(False, None, owing)
        payout = Payout(self.current_week, self.next_recipient(), self.pot)
        self.payouts.append(payout)
        if not self.is_complete:
            self.current_week += 1
        self._paid = {m: Decimal("0.00") for m in self._members}
        return CloseResult(True, payout, {})

        # ---- persistence ----
    def to_dict(self) -> dict:
        return {
            "weekly_amount": str(self.weekly_amount),
            "members": list(self._members),
            "paid": {m: str(v) for m, v in self._paid.items()},
            "current_week": self.current_week,
            "payouts": [{"week": p.week, "member": p.member, "amount": str(p.amount)}
                        for p in self.payouts],
            "started": self._started,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SusuGroup":
        group = cls(data["weekly_amount"])
        group._members = list(data["members"])
        group._paid = {m: Decimal(v) for m, v in data["paid"].items()}
        group.current_week = data["current_week"]
        group.payouts = [Payout(p["week"], p["member"], Decimal(p["amount"]))
                         for p in data["payouts"]]
        group._started = data["started"]
        return group