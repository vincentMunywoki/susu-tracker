import shlex
from pathlib import Path

from . import storage
from .errors import SusuError
from .group import SusuGroup
from .money import fmt

DATA_FILE = Path("susu.json")

HELP = """Commands:
  create <weekly_amount>        create the group, e.g. create 50.00
  add <name>                    add a member (before any payment is recorded)
  pay <name> <amount> [week]    record a contribution (use quotes for names with spaces)
  close                         close the current week
  report                        show status and payout history
  reset                         delete the group and start over
  help | quit"""


def format_report(group: SusuGroup) -> str:
    lines = [f"Weekly contribution: GHS {fmt(group.weekly_amount)} | "
             f"Members: {len(group.members)} | Pot: GHS {fmt(group.pot)}"]
    if group.is_complete:
        lines.append("Cycle complete: every member has received a payout.")
    else:
        lines.append(f"Current week: {group.current_week} "
                     f"(payout goes to: {group.next_recipient() or 'n/a'})")
        full = group.paid_in_full()
        lines.append("Paid in full: " + (", ".join(full) if full else "nobody yet"))
        owing = group.outstanding()
        if owing:
            lines.append("Owing:")
            lines += [f"  {m} owes GHS {fmt(a)}" for m, a in owing.items()]
        else:
            lines.append("Owing: nobody")
    lines.append("Payout history:")
    if group.payouts:
        lines += [f"  Week {p.week}: {p.member} received GHS {fmt(p.amount)}"
                  for p in group.payouts]
    else:
        lines.append("  (none yet)")
    return "\n".join(lines)


def _need_group(group):
    if group is None:
        raise SusuError("No group yet. Use: create <weekly_amount>")
    return group


def _need_args(args, low, high, usage):
    if not low <= len(args) <= high:
        raise SusuError(f"Usage: {usage}")


def handle(group, cmd, args):
    """Run one command. Returns (group, message)."""
    if cmd == "create":
        _need_args(args, 1, 1, "create <weekly_amount>")
        if group is not None:
            raise SusuError("A group already exists. Use 'reset' first.")
        group = SusuGroup(args[0])
        return group, f"Group created: GHS {fmt(group.weekly_amount)} per member per week."
    if cmd == "reset":
        return None, "Group deleted."
    if cmd == "help":
        return group, HELP

    group = _need_group(group)
    if cmd == "add":
        _need_args(args, 1, 99, "add <name>")
        name = group.add_member(" ".join(args))
        return group, f"Added {name} (position {len(group.members)})."
    if cmd == "pay":
        _need_args(args, 2, 3, "pay <name> <amount> [week]")
        week = None
        if len(args) == 3:
            try:
                week = int(args[2])
            except ValueError:
                raise SusuError("Week must be a whole number.") from None
        left = group.record_contribution(args[0], args[1], week)
        status = "paid in full" if left == 0 else f"still owes GHS {fmt(left)}"
        return group, f"Recorded. {args[0]} {status}."
    if cmd == "close":
        result = group.close_week()
        if result.closed:
            p = result.payout
            msg = f"Week {p.week} closed. {p.member} receives GHS {fmt(p.amount)}."
            if group.is_complete:
                return group, msg + " Cycle complete!"
            return group, msg + f" Week {group.current_week} begins; next: {group.next_recipient()}."
        lines = ["Week cannot close yet. Outstanding:"]
        lines += [f"  {m} owes {fmt(a)}" for m, a in result.owing.items()]
        return group, "\n".join(lines)
    if cmd == "report":
        return group, format_report(group)
    raise SusuError(f"Unknown command '{cmd}'. Type 'help'.")


def run(path: Path = DATA_FILE) -> None:
    group = storage.load(path)
    print("Susu Group Tracker. Type 'help' for commands.")
    while True:
        try:
            line = input("susu> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        try:
            parts = shlex.split(line)
        except ValueError as exc:
            print(f"Error: {exc}")
            continue
        if not parts:
            continue
        cmd, args = parts[0].lower(), parts[1:]
        if cmd in ("quit", "exit"):
            break
        try:
            group, message = handle(group, cmd, args)
            storage.save(group, path)
            print(message)
        except SusuError as exc:
            print(f"Error: {exc}")