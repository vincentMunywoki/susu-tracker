import json
from pathlib import Path

from .group import SusuGroup


def load(path: Path):
    if not path.exists():
        return None
    return SusuGroup.from_dict(json.loads(path.read_text(encoding="utf-8")))


def save(group, path: Path) -> None:
    if group is None:
        path.unlink(missing_ok=True)
        return
    path.write_text(json.dumps(group.to_dict(), indent=2), encoding="utf-8")