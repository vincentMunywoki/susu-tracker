# Notes

## Assumptions and decisions
- **Money**: `Decimal`, never floats; max 2 decimal places; floats are rejected.
- **Names**: unique, case-insensitive, whitespace trimmed.
- **Payout order** = order members were added.
- **Adding members**: allowed only until the first contribution is recorded.
  Reason: a late joiner would change the pot size and the payout order mid-cycle.
- **Contributions** are accepted only for the current week (past weeks are fully paid,
  future weeks are not open). Overpaying a week is rejected.
- **Closing with debts** changes nothing and reports who owes what.
- **Cycle length** = number of members. After the last member is paid, the cycle is
  complete and further payments/closes are rejected.
- **Cannot close** a group with zero members.
- **Business logic** lives in `group.py` with no I/O so it is easy to test.

## What I would improve with more time
- Allow starting a new cycle after one completes.
- Allow late joiners at the end of the order (once a cycle ends) or with a catch-up rule.
- Keep an audit log of every contribution (timestamp, amount).
- Non-interactive subcommands (`susu pay Ama 50`) and a small HTTP API.
- Atomic file writes to protect against corrupted data.