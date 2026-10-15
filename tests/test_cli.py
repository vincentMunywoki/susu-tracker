import pytest

from susu.cli import format_report, handle
from susu.errors import SusuError


def test_cli_week_cannot_close_message_and_report():
    group, _ = handle(None, "create", ["50.00"])
    for name in ("Ama", "Esi"):
        handle(group, "add", [name])
    handle(group, "pay", ["Ama", "50"])
    handle(group, "pay", ["Esi", "30"])
    _, message = handle(group, "close", [])
    assert "Esi owes 20.00" in message
    assert "Paid in full: Ama" in format_report(group)


def test_cli_requires_group():
    with pytest.raises(SusuError):
        handle(None, "add", ["Ama"])