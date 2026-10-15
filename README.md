# Susu Group Tracker

A small command-line program that manages one rotating savings group (susu) in GHS.

## Requirements
Python 3.11+ (tested on Windows 11).

## Setup (Windows PowerShell)
```powershell
git clone <repo-url>
cd susu-tracker
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

## Run
```powershell
python -m susu
```
Commands: `create`, `add`, `pay`, `close`, `report`, `reset`, `help`, `quit`.
Data is saved to `susu.json` in the current folder.

Example session:
```
susu> create 50.00
susu> add Ama
susu> add Kofi
susu> pay Ama 50
susu> pay Kofi 30
susu> close
Week cannot close yet. Outstanding:
  Kofi owes 20.00
```

## Run the tests
```powershell
python -m pytest -v
```

## Project layout
- `susu/money.py`: exact money parsing (Decimal)
- `susu/group.py`: all business rules (no I/O)
- `susu/storage.py`: JSON save/load
- `susu/cli.py`: command parsing and report formatting
- `tests/`: automated tests