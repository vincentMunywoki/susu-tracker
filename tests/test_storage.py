from decimal import Decimal

from susu import storage
from susu.group import SusuGroup


def test_save_and_load_roundtrip(tmp_path):
    group = SusuGroup("50.00")
    group.add_member("Ama")
    group.record_contribution("Ama", "20.50")
    path = tmp_path / "susu.json"
    storage.save(group, path)
    loaded = storage.load(path)
    assert loaded.members == ("Ama",)
    assert loaded.outstanding() == {"Ama": Decimal("29.50")}